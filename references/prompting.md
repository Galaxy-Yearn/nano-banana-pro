# Prompting

Use this as an on-demand reference when the prompt needs to be more precise and efficient.

## Pattern

`[ratio/size], [asset type], [subject], [composition], [style], [lighting/color], [hard constraints]`

Keep one sentence unless there are multiple input images. Put ratio and size in the prompt when relevant, for example `1:1`, `4:5`, `16:9`, `1K`, `2K`, or `4K`.

Use only `1K`, `2K`, or `4K` for size. Do not use `512`, `0.5K`, or any other size token.

## Edits

Reference input images by order:

`Edit input image 1 into a 4:5 catalog photo, preserve exact product shape/logo/color, off-white seamless background, soft studio shadow.`

For composition:

`16:9 ad, input image 1 product, input image 2 package, preserve brand identity, premium kitchen scene, warm morning light, no extra text.`

## Text

Quote exact visible text and state placement:

`4:5 poster, exact title "OPEN STUDIO" centered top, bold condensed sans, orange risograph texture.`

Avoid long negative prompt blocks. Use direct constraints: `no text`, `transparent background`, `preserve face identity`, `change only background`.
