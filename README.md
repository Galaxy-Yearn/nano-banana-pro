# Nano Banana Pro Codex Skill

Codex skill for generating and editing images with a Nano Banana / Gemini-compatible image API. It includes a small Python script that reads local credentials from `.env`, sends text and optional input images to the configured model, and saves one image to the path requested by Codex.

## What It Does

- Generate an image from a compact text prompt.
- Edit one or more local reference images.
- Compose multiple input images into one output image.
- Infer `aspect_ratio` and `image_size` from prompt text such as `1:1`, `4:5`, `16:9`, `1K`, `2K`, or `4K`.
- Save exactly one output image per request.
- Let Codex choose the output path with `--filename`.

## Requirements

- Codex with local skill support.
- `uv` available on `PATH`.
- A Nano Banana / Gemini-compatible API key.
- A compatible API base URL.
- Python dependencies are declared inline in `scripts/generate_image.py` and installed by `uv run`.

## Install

Clone this repository into your Codex skills directory:

```bash
git clone https://github.com/<your-user>/nano-banana-pro ~/.codex/skills/nano-banana-pro
```

On Windows, the Codex skills directory is usually:

```powershell
git clone https://github.com/<your-user>/nano-banana-pro $env:USERPROFILE\.codex\skills\nano-banana-pro
```

If `CODEX_HOME` is set, install under:

```bash
$CODEX_HOME/skills/nano-banana-pro
```

## Configure

Create a local `.env` from the example:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Set:

```env
NANOBANANA_API_KEY=your_api_key_here
NANOBANANA_BASE_URL=https://your-compatible-base-url.example
NANOBANANA_MODEL=gemini-3-pro-image-preview
```

`.env` is ignored by git. Do not commit real API keys.

## Usage

Codex should invoke the skill when asked to generate, edit, compose, or refine images. The skill instructions are in `SKILL.md`.

Manual text-to-image call:

```bash
uv run scripts/generate_image.py --prompt "1:1 app icon, friendly banana astronaut, tactile 3D clay, warm yellow suit, clean white background, no text." --filename "banana-icon.png"
```

Manual image edit:

```bash
uv run scripts/generate_image.py --prompt "Edit input image 1 into a 4:5 catalog photo, preserve exact product shape/logo/color, off-white seamless background, soft studio shadow." --filename "catalog.png" -i "/path/to/product.png"
```

Manual multi-image composition:

```bash
uv run scripts/generate_image.py --prompt "16:9 ad, input image 1 product, input image 2 package, preserve brand identity, premium kitchen scene, warm morning light, no extra text." --filename "ad.png" -i product.png -i package.png
```

Override the configured model for one call:

```bash
uv run scripts/generate_image.py --prompt "9:16 phone wallpaper, calm glass greenhouse at sunrise, soft mist, botanical detail, no text." --filename "wallpaper.png" --model "gemini-3.2-pro-image-preview"
```

## Prompting

Use short, concrete prompts:

```text
[ratio/size], [asset type], [subject], [composition], [style], [lighting/color], [hard constraints]
```

Examples:

```text
16:9 cinematic product hero, matte black espresso machine on travertine counter, morning side light, shallow depth of field, premium editorial, no text.
```

```text
Edit input image 1 into a 4:5 catalog photo, preserve exact product shape/logo/color, off-white seamless background, soft studio shadow.
```

For more prompt guidance, see `references/prompting.md`.

## Constraints

- One output image per request.
- Supported size tokens are `1K`, `2K`, and `4K`.
- Do not use `512`, `0.5K`, or other size tokens.
- Input image count is limited to 14.
- Output location is controlled by `--filename`.
- `NANOBANANA_BASE_URL` is passed as-is; the script does not append endpoint suffixes.
- The API must be compatible with the `google-genai` client behavior used by the script.

## Repository Contents

- `SKILL.md`: Codex skill instructions.
- `scripts/generate_image.py`: image generation/editing script.
- `references/prompting.md`: concise prompting reference.
- `agents/openai.yaml`: Codex UI metadata.
- `.env.example`: safe configuration template.
- `.gitignore`: excludes local secrets and logs.

## Security

Keep credentials only in `.env`. If a real key is ever committed, revoke it immediately and rotate the key.
