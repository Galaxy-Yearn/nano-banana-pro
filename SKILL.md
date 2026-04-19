---
name: nano-banana-pro
description: Generate, edit, compose, and refine raster images using Nano Banana / Gemini-compatible image generation through the bundled script. Use when Codex needs to create an image file from text, edit or restyle local images, combine references, make product shots, icons, posters, infographics, wallpapers, or other visual assets using API key, base URL, and model from the skill-local .env file.
---

# Nano Banana Pro

Use `scripts/generate_image.py` to generate or edit local images. The script reads API key, base URL, and default model from this skill's `.env`.

## Workflow

1. Write one compact production prompt that states the image directly.
2. Put ratio or size in the prompt only when it matters. If specifying size, use exactly `1K`, `2K`, or `4K`; never use `512`, `0.5K`, pixel dimensions, or vague size words.
3. Run the script from this skill directory with `uv run scripts/generate_image.py`. If a timeout is needed, use `timeout_ms: 900000`.
4. Return the single `Saved image:` path.
5. Generate exactly one output image per request. Do not use this skill for output batches.

## Prompt Rule

Use the shortest prompt that fully specifies the result. Prefer concrete nouns, composition, and hard constraints over generic quality words.

Default form: `[ratio/size] [asset type], [subject], [composition], [style/medium], [lighting/color], [hard constraints].`

Keep one sentence unless the task has multiple input images or exact visible text. Do not add filler such as `high quality`, `masterpiece`, `ultra detailed`, or long negative prompts.

Examples:

- `1:1 app icon, friendly banana astronaut, tactile 3D clay, warm yellow suit, clean white background, no text.`
- `16:9 cinematic product hero, matte black espresso machine on travertine counter, morning side light, shallow depth of field, premium editorial, no text.`
- `Edit input image 1 into a 4:5 catalog photo, preserve exact product shape/logo/color, off-white seamless background, soft studio shadow.`

For edits or composition, name each input image by order and state what to preserve. The script infers `aspect_ratio` and `image_size` from prompt tokens such as `1:1`, `4:5`, `16:9`, `1K`, `2K`, or `4K`. Use `--aspect-ratio` or `--resolution` only to override ambiguity.

Valid explicit image sizes are exactly `1K`, `2K`, and `4K`. Omit size when the user does not need to control it.

Read `references/prompting.md` only for high-risk prompts: product or identity preservation, multi-image composition, exact text/layout, transparent icons/logos, posters, or infographics. Do not read it for simple text-to-image tasks.

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
