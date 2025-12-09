# Image Examples

Markdown-svg supports images using standard markdown syntax.

## Basic Image

![Mountain landscape](https://picsum.photos/seed/mountain/400/200)

## Image with Alt Text

Alt text is important for accessibility:

![A beautiful sunset over the ocean](https://picsum.photos/seed/sunset/400/200)

## Multiple Images

You can include several images in a document:

![Forest path](https://picsum.photos/seed/forest/400/200)

![City skyline](https://picsum.photos/seed/city/400/200)

![Desert dunes](https://picsum.photos/seed/desert/400/200)

## Images with Text

Images work naturally alongside other content:

The image below shows a peaceful lake scene. Notice how the text wraps normally before and after the image.

![Peaceful lake](https://picsum.photos/seed/lake/400/200)

This text appears after the image, continuing the document flow.

## Notes

- Images are rendered as SVG `<image>` elements
- External URLs must be accessible to the SVG viewer
- Default: full-width with 16:9 aspect ratio (configurable via style)

