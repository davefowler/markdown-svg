# Image Examples

Markdown-svg supports images with flexible sizing options.

## Basic Image (Full Width)

Images default to full container width.  By default they're fetched to get the aspect ratio as in SVG both height and width have to be explicitly set. 

```markdown
![Mountain landscape](https://picsum.photos/seed/mountain/800/400)
```

![Mountain landscape](https://picsum.photos/seed/mountain/800/400)

## Explicit Dimensions

To save time on fetching, use `{width=X height=Y}` after the markdown image syntax for precise control:

```markdown
![Sunset](https://picsum.photos/seed/sunset/400/200){width=300 height=150}
```

![Sunset](https://picsum.photos/seed/sunset/400/200){width=300 height=150}

## Width Only

Specify just width and height auto-calculates from the fetched image's actual aspect ratio:

![Forest](https://picsum.photos/seed/forest/600/400){width=400}


## Aspect Ratio

If we cannot find the image or its size, there's a fall back to `image_fallback_aspect_ratio`.  You can enforce using this fallback (and skip fetching the image) by setting `image_enforce_aspect_ratio: true`.


## Multiple Images

Images flow naturally in the document:

![City skyline](https://picsum.photos/seed/city/800/400)

![Peaceful lake](https://picsum.photos/seed/lake/800/400)

## Sizing Priority

1. **Explicit dimensions** from markdown `{width=X height=Y}`
2. **Fetched dimensions** from actual image (with PIL+requests)
3. **Style defaults** (`image_width`, `image_height`)
4. **Fallback** full width with `image_fallback_aspect_ratio` (16:9)

Set `image_enforce_aspect_ratio=True` to skip fetching and always use the fallback ratio (faster rendering).

## Technical Notes

- Images render as SVG `<image>` elements
- With `pillow` + `requests` installed, dimensions are fetched automatically
- URL mapping available for CDN/asset path rewriting via `image_url_mapper`
- Local files are detected quickly without network requests

