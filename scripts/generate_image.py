#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Generate or edit images with a Gen AI compatible client.

The script reads configuration from the skill folder's local .env file.
"""

from __future__ import annotations

import argparse
import io
import json
import mimetypes
import re
import sys
from pathlib import Path
from typing import Any

from PIL import Image as PILImage

SKILL_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = SKILL_DIR / ".env"

DEFAULT_MODEL = "gemini-3-pro-image-preview"
DEFAULT_MAX_INPUT_IMAGES = 14
SUPPORTED_IMAGE_SIZES = ("1K", "2K", "4K")

SUPPORTED_OUTPUT_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}

ASPECT_RATIO_TERMS = (
    (re.compile(r"(?i)(?:^|[\s,;(\[])(1\s*[:\uFF1A]\s*1)(?:$|[\s,;)\]])"), "1:1"),
    (re.compile(r"(?i)(?:^|[\s,;(\[])(2\s*[:\uFF1A]\s*3)(?:$|[\s,;)\]])"), "2:3"),
    (re.compile(r"(?i)(?:^|[\s,;(\[])(3\s*[:\uFF1A]\s*2)(?:$|[\s,;)\]])"), "3:2"),
    (re.compile(r"(?i)(?:^|[\s,;(\[])(3\s*[:\uFF1A]\s*4)(?:$|[\s,;)\]])"), "3:4"),
    (re.compile(r"(?i)(?:^|[\s,;(\[])(4\s*[:\uFF1A]\s*3)(?:$|[\s,;)\]])"), "4:3"),
    (re.compile(r"(?i)(?:^|[\s,;(\[])(4\s*[:\uFF1A]\s*5)(?:$|[\s,;)\]])"), "4:5"),
    (re.compile(r"(?i)(?:^|[\s,;(\[])(5\s*[:\uFF1A]\s*4)(?:$|[\s,;)\]])"), "5:4"),
    (re.compile(r"(?i)(?:^|[\s,;(\[])(9\s*[:\uFF1A]\s*16)(?:$|[\s,;)\]])"), "9:16"),
    (re.compile(r"(?i)(?:^|[\s,;(\[])(16\s*[:\uFF1A]\s*9)(?:$|[\s,;)\]])"), "16:9"),
    (re.compile(r"(?i)(?:^|[\s,;(\[])(21\s*[:\uFF1A]\s*9)(?:$|[\s,;)\]])"), "21:9"),
    (re.compile(r"(?i)\b(square|avatar|icon|logo|sticker)\b|\u6B63\u65B9\u5F62|\u65B9\u56FE|\u5934\u50CF|\u56FE\u6807|\u5FBD\u6807"), "1:1"),
    (re.compile(r"(?i)\b(vertical|portrait|phone wallpaper|story|reel)\b|\u7AD6\u5C4F|\u7AD6\u7248|\u624B\u673A\u58C1\u7EB8"), "9:16"),
    (re.compile(r"(?i)\b(horizontal|landscape|widescreen|desktop wallpaper|hero banner)\b|\u6A2A\u5C4F|\u6A2A\u7248|\u5BBD\u5C4F|\u684C\u9762\u58C1\u7EB8"), "16:9"),
)


def warn(message: str) -> None:
    print(f"Warning: {message}", file=sys.stderr)


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def parse_env_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]
    return value


def read_env_file(path: Path = ENV_FILE) -> dict[str, str]:
    env_values: dict[str, str] = {}
    if not path.exists():
        return env_values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
            continue
        env_values[key] = parse_env_value(value)
    return env_values


def clean_env(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def normalize_aspect_ratio(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = re.sub(r"\s+", "", value.strip().replace("\uFF1A", ":"))
    return normalized or None


def normalize_resolution(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().upper()
    if normalized in {"1K", "1024"}:
        return "1K"
    if normalized in {"2K", "2048"}:
        return "2K"
    if normalized in {"4K", "4096"}:
        return "4K"
    if normalized in {"0.5K", ".5K", "512"}:
        return "512"
    return normalized or None


def infer_aspect_ratio(prompt: str) -> str | None:
    for pattern, aspect_ratio in ASPECT_RATIO_TERMS:
        if pattern.search(prompt):
            return aspect_ratio
    return None


def infer_resolution(prompt: str) -> str | None:
    match = re.search(r"(?i)(?<![\w.])(0\.5k|\.5k|512|1k|2k|4k|1024|2048|4096)(?![\w])", prompt)
    if not match:
        return None
    return normalize_resolution(match.group(1))


def read_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        try:
            prompt = Path(args.prompt_file).read_text(encoding="utf-8")
        except OSError as exc:
            fail(f"Could not read prompt file '{args.prompt_file}': {exc}")
    else:
        prompt = args.prompt

    prompt = prompt.strip()
    if not prompt:
        fail("Prompt is empty.")
    return prompt


def get_runtime_settings(
    args: argparse.Namespace,
    env_values: dict[str, str],
) -> dict[str, str | None]:
    return {
        "api_key": clean_env(env_values.get("NANOBANANA_API_KEY")),
        "base_url": clean_env(env_values.get("NANOBANANA_BASE_URL")),
        "model": args.model or clean_env(env_values.get("NANOBANANA_MODEL")) or DEFAULT_MODEL,
    }


def choose_image_controls(
    args: argparse.Namespace,
    prompt: str,
) -> tuple[str | None, str | None, str | None, str | None]:
    aspect_source = None
    resolution_source = None

    aspect_ratio = normalize_aspect_ratio(args.aspect_ratio)
    if aspect_ratio:
        aspect_source = "flag"
    else:
        aspect_ratio = infer_aspect_ratio(prompt)
        if aspect_ratio:
            aspect_source = "prompt"

    resolution = normalize_resolution(args.resolution)
    if resolution:
        resolution_source = "flag"
    else:
        resolution = infer_resolution(prompt)
        if resolution:
            resolution_source = "prompt"

    return aspect_ratio, aspect_source, resolution, resolution_source


def validate_aspect_ratio(aspect_ratio: str | None) -> None:
    if aspect_ratio is None:
        return
    if not re.match(r"^[1-9][0-9]*:[1-9][0-9]*$", aspect_ratio):
        fail(f"Invalid aspect ratio '{aspect_ratio}'. Use a ratio like 16:9.")


def validate_resolution(resolution: str | None) -> None:
    if resolution is None:
        return
    if resolution not in SUPPORTED_IMAGE_SIZES:
        supported = ", ".join(SUPPORTED_IMAGE_SIZES)
        fail(
            f"Invalid image size '{resolution}'. This Gemini image workflow supports "
            f"{supported}. Use one of those values, or omit --resolution / size text to use "
            "the model default."
        )


def load_input_image(path_text: str) -> tuple[Path, bytes, str, int, int]:
    path = Path(path_text)
    if not path.exists():
        fail(f"Input image not found: {path_text}")
    if not path.is_file():
        fail(f"Input image is not a file: {path_text}")

    with PILImage.open(path) as image:
        width, height = image.size

    mime_type = mimetypes.guess_type(str(path))[0] or "image/png"
    return path, path.read_bytes(), mime_type, width, height


def build_contents(prompt: str, loaded_images: list[tuple[Path, bytes, str, int, int]], types: Any) -> list[Any]:
    parts = [types.Part.from_text(text=prompt)]
    for index, (path, data, mime_type, _width, _height) in enumerate(loaded_images, start=1):
        parts.append(types.Part.from_text(text=f"Input image {index}: {path.name}"))
        parts.append(types.Part.from_bytes(data=data, mime_type=mime_type))
    return [types.Content(role="user", parts=parts)]


def build_config(
    aspect_ratio: str | None,
    resolution: str | None,
    types: Any,
) -> Any:
    image_config_kwargs: dict[str, str] = {}
    if aspect_ratio:
        image_config_kwargs["aspect_ratio"] = aspect_ratio
    if resolution:
        image_config_kwargs["image_size"] = resolution

    config_kwargs: dict[str, Any] = {"response_modalities": ["TEXT", "IMAGE"]}
    if image_config_kwargs:
        config_kwargs["image_config"] = types.ImageConfig(**image_config_kwargs)
    return types.GenerateContentConfig(**config_kwargs)


def build_client(settings: dict[str, str | None]) -> Any:
    from google import genai
    from google.genai import types

    http_options_kwargs: dict[str, str] = {}
    if settings["base_url"]:
        http_options_kwargs["base_url"] = settings["base_url"]

    http_options = (
        types.HttpOptions(**http_options_kwargs)
        if http_options_kwargs
        else None
    )
    if http_options is None:
        return genai.Client(api_key=settings["api_key"])
    return genai.Client(api_key=settings["api_key"], http_options=http_options)


def normalize_output_path(path: Path) -> Path:
    if not path.suffix:
        return path.with_suffix(".png")
    if path.suffix.lower() not in SUPPORTED_OUTPUT_SUFFIXES:
        warn(f"Unsupported output extension '{path.suffix}'. Saving as PNG instead.")
        return path.with_suffix(".png")
    return path


def flatten_alpha(image: PILImage.Image) -> PILImage.Image:
    if image.mode != "RGBA":
        return image.convert("RGB")
    background = PILImage.new("RGB", image.size, (255, 255, 255))
    background.paste(image, mask=image.split()[3])
    return background


def coerce_pil_image(image: Any) -> PILImage.Image:
    if isinstance(image, PILImage.Image):
        return image

    for attr in ("pil_image", "_pil_image"):
        candidate = getattr(image, attr, None)
        if isinstance(candidate, PILImage.Image):
            return candidate

    for attr in ("image_bytes", "_image_bytes", "data"):
        candidate = getattr(image, attr, None)
        if isinstance(candidate, (bytes, bytearray)):
            with PILImage.open(io.BytesIO(candidate)) as pil_image:
                return pil_image.copy()

    save_method = getattr(image, "save", None)
    if callable(save_method):
        buffer = io.BytesIO()
        save_method(buffer)
        buffer.seek(0)
        with PILImage.open(buffer) as pil_image:
            return pil_image.copy()

    raise TypeError(f"Unsupported image object returned by SDK: {type(image)!r}")


def save_image(image: Any, output_path: Path) -> Path:
    image = coerce_pil_image(image)
    suffix = output_path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        flatten_alpha(image).save(str(output_path), "JPEG", quality=95)
    elif suffix == ".webp":
        image.save(str(output_path), "WEBP", quality=95)
    else:
        if image.mode not in {"RGB", "RGBA"}:
            has_alpha = "A" in image.getbands()
            image = image.convert("RGBA" if has_alpha else "RGB")
        image.save(str(output_path), "PNG")
    return output_path.resolve()


def dump_response(response: Any, path_text: str) -> None:
    path = Path(path_text)
    if hasattr(response, "model_dump_json"):
        text = response.model_dump_json(indent=2)
    elif hasattr(response, "to_json_dict"):
        text = json.dumps(response.to_json_dict(), indent=2, ensure_ascii=False)
    else:
        text = repr(response)
    path.write_text(text, encoding="utf-8")
    print(f"Raw response saved: {path.resolve()}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate or edit images with a Gen AI compatible client."
    )
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", "-p", help="Compact image prompt.")
    prompt_group.add_argument("--prompt-file", help="UTF-8 text file containing the prompt.")
    parser.add_argument("--filename", "-f", required=True, help="Output image filename.")
    parser.add_argument(
        "--input-image",
        "-i",
        action="append",
        dest="input_images",
        metavar="IMAGE",
        help="Input image for editing or composition. Repeat for multiple images.",
    )
    parser.add_argument("--model", "-m", help=f"Model ID. Default: {DEFAULT_MODEL}.")
    parser.add_argument("--resolution", "-r", help="Image size such as 1K, 2K, or 4K.")
    parser.add_argument("--aspect-ratio", "-a", help="Aspect ratio such as 1:1, 4:5, 9:16, 16:9.")
    parser.add_argument("--dump-response-json", help="Write raw SDK response for troubleshooting.")
    return parser.parse_args()


def main() -> None:
    env_values = read_env_file()
    args = parse_args()
    prompt = read_prompt(args)
    settings = get_runtime_settings(args, env_values)
    model = settings["model"] or DEFAULT_MODEL

    if not settings["api_key"]:
        fail(f"No API key found. Set NANOBANANA_API_KEY in {ENV_FILE}.")
    if not settings["base_url"]:
        fail(f"No base URL found. Set NANOBANANA_BASE_URL in {ENV_FILE}.")

    loaded_images = []
    if args.input_images:
        if len(args.input_images) > DEFAULT_MAX_INPUT_IMAGES:
            fail(
                f"Too many input images ({len(args.input_images)}). "
                f"Maximum is {DEFAULT_MAX_INPUT_IMAGES}."
            )

        for index, image_path in enumerate(args.input_images, start=1):
            loaded = load_input_image(image_path)
            loaded_images.append(loaded)
            path, _data, _mime_type, width, height = loaded
            print(f"Loaded input image {index}: {path} ({width}x{height})")

    aspect_ratio, aspect_source, resolution, resolution_source = choose_image_controls(
        args=args,
        prompt=prompt,
    )
    validate_aspect_ratio(aspect_ratio)
    validate_resolution(resolution)

    output_path = normalize_output_path(Path(args.filename))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from google.genai import types

        client = build_client(settings)
        contents = build_contents(prompt, loaded_images, types)
        config = build_config(aspect_ratio, resolution, types)

        print(f"Model: {model}")
        if aspect_ratio:
            print(f"Aspect ratio: {aspect_ratio}" + (f" ({aspect_source})" if aspect_source else ""))
        if resolution:
            print(f"Resolution: {resolution}" + (f" ({resolution_source})" if resolution_source else ""))
        print("Editing with input images..." if loaded_images else "Generating image from text...")

        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )

        if args.dump_response_json:
            dump_response(response, args.dump_response_json)

        saved_image: Path | None = None
        image_count = 0
        for part in response.parts or []:
            if part.text is not None:
                text = part.text.strip()
                if text:
                    print(f"Model response: {text}")
                continue

            image = part.as_image()
            if image is None:
                continue

            image_count += 1
            if image_count > 1:
                fail(
                    "This workflow supports exactly one output image per request. "
                    "The model returned multiple images."
                )
            saved_image = save_image(image, output_path)

        if saved_image is None:
            fail("No image was generated in the response.")

        print(f"Saved image: {saved_image}")

    except Exception as exc:
        fail(f"Image generation failed: {exc}")


if __name__ == "__main__":
    main()
