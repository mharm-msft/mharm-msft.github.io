"""Rasterize Tron disc favicon to PNG variants + ICO.

Stdlib + Pillow only. Avoids any SVG renderer (cairosvg, rsvg) — draws the
disc primitives directly with Pillow so it works on a stock Windows Python.
"""
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path

OUT = Path(__file__).parent
BG       = (0, 0, 0, 255)
CYAN     = (0, 229, 255, 255)
ICE      = (125, 249, 255, 255)
ORANGE   = (255, 107, 0, 255)
WHITE    = (255, 255, 255, 255)

def draw_disc(size: int) -> Image.Image:
    """Draw at 4x supersample then downscale for crisp anti-aliasing."""
    s = size * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # bezel
    d.ellipse([0, 0, s-1, s-1], fill=BG)

    # outer cyan ring
    rw_outer = max(2, s // 22)
    d.ellipse(
        [rw_outer, rw_outer, s-1-rw_outer, s-1-rw_outer],
        outline=CYAN, width=rw_outer,
    )

    # inner ring
    rw_inner = max(1, s // 36)
    inset = int(s * 0.27)
    d.ellipse(
        [inset, inset, s-1-inset, s-1-inset],
        outline=CYAN, width=rw_inner,
    )

    # core disc
    core_inset = int(s * 0.36)
    # radial-ish glow: draw 3 concentric fills
    for r, color in [(0.36, (0, 61, 77, 255)),
                     (0.40, CYAN),
                     (0.44, ICE)]:
        ci = int(s * r)
        d.ellipse([ci, ci, s-1-ci, s-1-ci], fill=color)

    # hot white center
    hot = int(s * 0.46)
    d.ellipse([hot, hot, s-1-hot, s-1-hot], fill=WHITE)

    # Clu orange notch at top (small arc)
    arc_w = max(2, s // 22)
    pad = arc_w // 2
    d.arc([pad, pad, s-1-pad, s-1-pad],
          start=-103, end=-77,
          fill=ORANGE, width=arc_w)

    # mild glow pass
    glow = img.filter(ImageFilter.GaussianBlur(radius=s/220))
    out = Image.alpha_composite(glow, img)

    return out.resize((size, size), Image.LANCZOS)


def main():
    # Standard favicon sizes
    sizes = [16, 32, 48, 64, 180, 192, 512]
    rendered = {}
    for sz in sizes:
        im = draw_disc(sz)
        rendered[sz] = im
        path = OUT / f"favicon-{sz}.png"
        if sz in (16, 32, 48):
            continue  # don't ship individual small PNGs (use .ico)
        im.save(path, optimize=True)
        print(f"WROTE {path.name} ({path.stat().st_size} B)")

    # Apple touch icon (iOS home-screen)
    apple = OUT / "apple-touch-icon.png"
    rendered[180].save(apple, optimize=True)
    print(f"WROTE {apple.name} ({apple.stat().st_size} B)")

    # Multi-size .ico
    ico = OUT / "favicon.ico"
    rendered[48].save(
        ico,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
        append_images=[rendered[16], rendered[32]],
    )
    print(f"WROTE {ico.name} ({ico.stat().st_size} B)")

if __name__ == "__main__":
    main()
