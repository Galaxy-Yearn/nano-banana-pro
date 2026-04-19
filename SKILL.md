---
name: nano-banana-pro
description: Generate, edit, compose, and refine raster images using Nano Banana / Gemini-compatible image generation through the bundled script. Use when Codex needs to create an image file from text, edit or restyle local images, combine references, make product shots, icons, posters, infographics, wallpapers, or other visual assets using API key, base URL, and model from the skill-local .env file.
---

# Nano Banana Pro

Use `scripts/generate_image.py` to generate or edit local images. The script reads API key, base URL, and default model from this skill's `.env`.

## Workflow

1. Write one compact prompt that directly states the desired image, including ratio or size when relevant.
2. Run the script from this skill directory with `uv run scripts/generate_image.py`. If the caller must set a timeout, use `timeout_ms: 900000`.
3. Return the single `Saved image:` path for the request.
4. Only use `1K`, `2K`, or `4K` for image size. Do not request or imply `512`, `0.5K`, or any other size in prompts or flags.
5. This workflow supports exactly one output image per request. Do not use it for multi-image output batches.

## Prompt Rule

Use the shortest prompt that fully specifies the result. Prefer concrete nouns and constraints over style padding.

Good structure: `[output type], [subject], [composition/ratio], [style or medium], [lighting/color], [must preserve or exclude].`

Examples:

- `1:1 app icon, friendly banana astronaut, tactile 3D clay, warm yellow suit, clean white background, no text.`
- `16:9 cinematic product hero, matte black espresso machine on travertine counter, morning side light, shallow depth of field, premium editorial, no text.`
- `Edit input image 1 into a 4:5 catalog photo, preserve exact product shape/logo/color, off-white seamless background, soft studio shadow.`

For edits or composition, name each input image by order and state what to preserve. Do not add long negative prompts unless needed.

The script infers `aspect_ratio` and `image_size` from the prompt when it sees values like `1:1`, `4:5`, `16:9`, `1K`, `2K`, or `4K`.

This skill only supports three image sizes: `1K`, `2K`, and `4K`.

Do not use `512`, `0.5K`, or any other size in prompts or flags. If size is ambiguous, use `--resolution` and set it to `1K`, `2K`, or `4K`.

Read `references/prompting.md` only when you need a more precise, efficient prompt, especially for edits, multi-image composition, or exact text/layout constraints.

## Commands

Generate:

```bash
uv run scripts/generate_image.py --prompt "1:1 app icon, friendly banana astronaut, tactile 3D clay, warm yellow suit, clean white background, no text." --filename "banana-icon.png"
```

Edit:

```bash
uv run scripts/generate_image.py --prompt "Edit input image 1 into a 4:5 catalog photo, preserve exact product shape/logo/color, off-white seamless background, soft studio shadow." --filename "catalog.png" -i "/path/to/product.png"
```

Future or alternate model:

```bash
uv run scripts/generate_image.py --prompt "9:16 phone wallpaper, calm glass greenhouse at sunrise, soft mist, botanical detail, no text." --filename "wallpaper.png" --model "gemini-3.2-pro-image-preview"
```

Compose:

```bash
uv run scripts/generate_image.py --prompt "16:9 lifestyle ad, use input image 1 as product and input image 2 as package, preserve brand identity, premium editorial kitchen scene, warm morning light, no extra text." --filename "ad.png" -i product.png -i package.png
```

Use `--prompt-file prompt.txt` for multiline prompts.

## Configuration

Set required and default values in `.env`:

- `NANOBANANA_API_KEY`
- `NANOBANANA_MODEL`
- `NANOBANANA_BASE_URL`

`NANOBANANA_BASE_URL` is passed as-is. The script does not append endpoint suffixes.

Use `--model`, `--aspect-ratio`, or `--resolution` only for per-call overrides. Output location is controlled by `--filename`.

For open-source distribution, keep real secrets in local `.env` only and commit `.env.example` instead.
