"""
Build PWA app icons (Costco red + blue).

Outputs (PNG):
  icons/icon-192.png            192x192  any
  icons/icon-512.png            512x512  any
  icons/icon-180.png            180x180  Apple Touch Icon
  icons/icon-192-maskable.png   192x192  maskable (safe-area padded)
  icons/icon-512-maskable.png   512x512  maskable (safe-area padded)
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

OUT = Path(__file__).parent / "icons"
OUT.mkdir(parents=True, exist_ok=True)

COSTCO_RED  = (227, 24, 55)    # #E31837
COSTCO_BLUE = (0,  93, 170)    # #005DAA
WHITE       = (255, 255, 255)


def find_bold_font(size: int):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def make_icon(size: int, maskable: bool = False) -> Image.Image:
    """
    Costco-inspired icon:
      - Blue background (full bleed)
      - Red diagonal stripe / band across the middle
      - White FS mark + small subtitle 'EXAM'
    For maskable variant we shrink content into ~80% safe zone.
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Background ------------------------------------------------------------
    if maskable:
        # full-bleed blue (icon must look fine when clipped to a circle)
        d.rectangle([0, 0, size, size], fill=COSTCO_BLUE)
    else:
        # rounded square blue background
        radius = int(size * 0.22)
        d.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=COSTCO_BLUE)

    # Diagonal red band -----------------------------------------------------
    band = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    band_h = int(size * 0.30)
    cy = size // 2
    bd.rectangle([-size, cy - band_h // 2, size * 2, cy + band_h // 2],
                 fill=COSTCO_RED)
    band = band.rotate(-22, resample=Image.BICUBIC, expand=False)
    img.alpha_composite(band)

    # If non-maskable we want the band clipped to the rounded square.
    if not maskable:
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [0, 0, size - 1, size - 1], radius=int(size * 0.22), fill=255
        )
        bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        bg.paste(img, (0, 0), mask=mask)
        img = bg
        d = ImageDraw.Draw(img)

    # Compute safe zone for content -----------------------------------------
    inset = int(size * 0.18) if maskable else int(size * 0.10)
    inner = (inset, inset, size - inset, size - inset)
    inner_w = inner[2] - inner[0]
    inner_h = inner[3] - inner[1]

    # 'FS' big text ---------------------------------------------------------
    fs_size = int(inner_h * 0.62)
    font_fs = find_bold_font(fs_size)
    text = "FS"
    bbox = d.textbbox((0, 0), text, font=font_fs)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    cx = inner[0] + (inner_w - tw) // 2 - bbox[0]
    cy = inner[1] + (inner_h - th) // 2 - bbox[1] - int(inner_h * 0.06)
    # Drop shadow
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((cx + max(2, size // 180), cy + max(2, size // 180)),
                                text, font=font_fs, fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=max(1, size // 200)))
    img.alpha_composite(shadow)
    d = ImageDraw.Draw(img)
    d.text((cx, cy), text, font=font_fs, fill=WHITE)

    # Subtitle 'EXAM' -------------------------------------------------------
    sub_size = int(inner_h * 0.14)
    font_sub = find_bold_font(sub_size)
    sub = "EXAM"
    bbox = d.textbbox((0, 0), sub, font=font_sub)
    sw, sh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    sx = inner[0] + (inner_w - sw) // 2 - bbox[0]
    sy = inner[3] - sh - bbox[1] - int(inner_h * 0.02)
    # red pill behind subtitle
    pad_x = int(sub_size * 0.6)
    pad_y = int(sub_size * 0.25)
    pill = (sx + bbox[0] - pad_x, sy + bbox[1] - pad_y,
            sx + bbox[0] + sw + pad_x, sy + bbox[1] + sh + pad_y)
    d.rounded_rectangle(pill, radius=int(sub_size * 0.6), fill=COSTCO_RED)
    d.text((sx, sy), sub, font=font_sub, fill=WHITE)

    return img


def save(img: Image.Image, name: str):
    path = OUT / name
    img.save(path, "PNG", optimize=True)
    print(f"  wrote {path}  ({path.stat().st_size:,} bytes)")


def main():
    print("Building icons in", OUT)
    save(make_icon(192, maskable=False), "icon-192.png")
    save(make_icon(512, maskable=False), "icon-512.png")
    save(make_icon(180, maskable=False), "icon-180.png")
    save(make_icon(192, maskable=True),  "icon-192-maskable.png")
    save(make_icon(512, maskable=True),  "icon-512-maskable.png")
    # also a generic favicon-sized one
    save(make_icon(64, maskable=False),  "icon-64.png")
    print("Done.")


if __name__ == "__main__":
    main()
