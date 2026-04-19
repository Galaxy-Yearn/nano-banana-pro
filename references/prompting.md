# Prompt Templates

Use this only when the default `SKILL.md` prompt rule is not precise enough. Pick one template, delete unused slots, and keep the final prompt compact.

## Product Or Identity Preservation

Use when an input image must remain recognizable and only controlled parts should change:

`Edit input image 1 into [target asset], preserve exact [identity/shape/logo/colors/material], change only [background/lighting/crop], [ratio], [finish], no extra text.`

Example:

`Edit input image 1 into a 4:5 catalog photo, preserve exact bottle shape, label, logo, colors, and material, change only background and lighting, off-white seamless set, soft studio shadow, no extra text.`

## Multi-Image Roles

Use when multiple references have different roles and should not be blended randomly:

`[ratio] [asset], use input image 1 only as [role], input image 2 only as [role], preserve [identity/brand details], [scene/composition], [lighting/color], no extra text.`

Example:

`16:9 lifestyle ad, use input image 1 only as espresso machine and input image 2 only as package, preserve logos, colors, and proportions, premium editorial kitchen counter, warm morning side light, no extra text.`

## Style Reference Only

Use when an input image should guide style, not content:

`[ratio] [asset], [new subject], use input image 1 as style reference only, do not copy its subject/layout/text, [palette/texture], no text.`

Example:

`16:9 editorial illustration, rainy noodle shop exterior at night, use input image 1 as style reference only, do not copy its subject/layout/text, muted teal palette, soft ink texture, no text.`

## Text

Use only when visible text is required. Quote exact text and give placement:

`[ratio] [asset], exact text "[TEXT]" at [placement], [font style], [layout], [color/material], no other text.`

Example:

`4:5 poster, exact text "OPEN STUDIO" centered top, bold condensed sans, single chair silhouette below, orange risograph texture, no other text.`

## Transparent Assets

Use when clean edges or transparent background matter:

`1:1 [sticker/icon/logo mark], [subject], centered readable silhouette, clean edge, [material/style], transparent background, no text.`

Example:

`1:1 transparent sticker, smiling corgi wizard, centered readable silhouette, clean die-cut edge, soft vinyl texture, transparent background, no text.`

## Structured Layout

Use when layout matters more than realism:

`[ratio] infographic, [topic], [number] panels, [flow direction], one simple visual per panel, minimal exact labels: "[label 1]", "[label 2]", "[label 3]", [palette], no extra text.`

Example:

`16:9 infographic, pour-over coffee workflow, 4 left-to-right panels, one simple icon per panel, minimal exact labels: "Grind", "Dose", "Bloom", "Pour", cream and espresso palette, no extra text.`
