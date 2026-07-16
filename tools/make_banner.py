#!/usr/bin/env python3
"""Generate the WinRecon README banner (assets/banner.png) with Pillow."""
import math
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "banner.png")

W, H = 1280, 420
SCALE = 2  # supersample for crisp edges
W2, H2 = W * SCALE, H * SCALE

BG0 = (10, 14, 20)
BG1 = (13, 22, 34)
TEAL = (40, 224, 200)
BLUE = (61, 139, 253)
WHITE = (230, 237, 243)
MUTED = (139, 152, 169)
CARD = (22, 27, 34)
BORDER = (44, 54, 68)

FONTS = "/System/Library/Fonts/Supplemental/"
SYS = "/System/Library/Fonts/"


def font(path, size, index=0):
    return ImageFont.truetype(path, size * SCALE, index=index)


F_BLACK = lambda s: font(FONTS + "Arial Black.ttf", s)          # noqa: E731
F_BOLD = lambda s: font(FONTS + "Arial Bold.ttf", s)            # noqa: E731
F_REG = lambda s: font(FONTS + "Arial.ttf", s)                  # noqa: E731
F_MONO = lambda s: font(SYS + "Menlo.ttc", s)                   # noqa: E731


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_text_tracked(d, xy, text, fnt, fill, tracking=0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill)
        w = d.textlength(ch, font=fnt)
        x += w + tracking * SCALE
    return x


def build():
    img = Image.new("RGB", (W2, H2), BG0)
    d = ImageDraw.Draw(img, "RGBA")

    # Diagonal gradient background.
    for y in range(H2):
        d.line([(0, y), (W2, y)], fill=lerp(BG0, BG1, y / H2))

    # Faint dot grid.
    step = 26 * SCALE
    for gy in range(0, H2, step):
        for gx in range(0, W2, step):
            d.ellipse([gx, gy, gx + 2, gy + 2], fill=(255, 255, 255, 10))

    # --- Right-side radar motif -------------------------------------------
    cx, cy = int(W2 * 0.80), int(H2 * 0.52)
    for i, r in enumerate(range(70, 240, 34)):
        alpha = 70 - i * 9
        d.ellipse([cx - r * SCALE, cy - r * SCALE, cx + r * SCALE, cy + r * SCALE],
                  outline=(40, 224, 200, max(alpha, 18)), width=SCALE)
    # crosshair
    d.line([(cx - 240 * SCALE, cy), (cx + 240 * SCALE, cy)],
           fill=(40, 224, 200, 26), width=SCALE)
    d.line([(cx, cy - 240 * SCALE), (cx, cy + 240 * SCALE)],
           fill=(40, 224, 200, 26), width=SCALE)
    # sweep wedge
    sweep = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sweep)
    R = 236 * SCALE
    sd.pieslice([cx - R, cy - R, cx + R, cy + R], -58, -18,
                fill=(40, 224, 200, 60))
    img.paste(Image.alpha_composite(img.convert("RGBA"), sweep).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    # blips
    for ang, rr, col in [(-35, 150, TEAL), (-70, 205, BLUE),
                         (-12, 110, TEAL), (-95, 175, MUTED)]:
        bx = cx + int(math.cos(math.radians(ang)) * rr * SCALE)
        by = cy + int(math.sin(math.radians(ang)) * rr * SCALE)
        d.ellipse([bx - 5 * SCALE, by - 5 * SCALE, bx + 5 * SCALE, by + 5 * SCALE],
                  fill=col)
        d.ellipse([bx - 10 * SCALE, by - 10 * SCALE, bx + 10 * SCALE, by + 10 * SCALE],
                  outline=col + (90,), width=SCALE)

    # --- Left accent bars --------------------------------------------------
    d.rectangle([0, 0, 8 * SCALE, H2], fill=TEAL)
    d.rectangle([8 * SCALE, 0, 12 * SCALE, H2], fill=BLUE)

    LX = 70 * SCALE

    # Eyebrow tag (pill sized to fit its tracked text)
    eyebrow = "CYBER RECON TOOLKIT"
    eb_font = F_BOLD(13)
    eb_track = 2
    eb_w = sum(d.textlength(c, font=eb_font) + eb_track * SCALE for c in eyebrow)
    d.rounded_rectangle([LX, 60 * SCALE, LX + eb_w + 34 * SCALE, 92 * SCALE],
                        radius=16 * SCALE, fill=(40, 224, 200, 28),
                        outline=(40, 224, 200, 120), width=SCALE)
    draw_text_tracked(d, (LX + 18 * SCALE, 68 * SCALE),
                      eyebrow, eb_font, TEAL, tracking=eb_track)

    # Title
    ty = 100 * SCALE
    x = draw_text_tracked(d, (LX - 2 * SCALE, ty), "Win", F_BLACK(78), TEAL)
    draw_text_tracked(d, (x + 4 * SCALE, ty), "Recon", F_BLACK(78), WHITE)

    # Tagline
    draw_text_tracked(d, (LX, 210 * SCALE),
                      "WINDOWS  INFORMATION  GATHERER", F_BOLD(22), WHITE,
                      tracking=3)

    # Description
    d.text((LX, 250 * SCALE),
           "Recon-grade system, network & security intelligence",
           font=F_REG(17), fill=MUTED)
    d.text((LX, 276 * SCALE),
           "for defenders, red teams and ethical hackers.",
           font=F_REG(17), fill=MUTED)

    # Feature chips
    chips = ["System", "Hardware", "Network", "Users", "Software",
             "Security Audit"]
    chx = LX
    chy = 320 * SCALE
    for c in chips:
        w = d.textlength(c, font=F_BOLD(13)) + 26 * SCALE
        d.rounded_rectangle([chx, chy, chx + w, chy + 30 * SCALE],
                            radius=15 * SCALE, fill=CARD,
                            outline=BORDER, width=SCALE)
        d.text((chx + 13 * SCALE, chy + 7 * SCALE), c, font=F_BOLD(13),
               fill=(200, 210, 222))
        chx += w + 10 * SCALE

    # Command hint
    d.text((LX, 372 * SCALE), "$ python winrecon.py", font=F_MONO(15), fill=TEAL)
    by = 372 * SCALE
    bx = LX + int(d.textlength("$ python winrecon.py", font=F_MONO(15))) + 16 * SCALE
    d.text((bx, by), "·  cross-platform demo mode  ·  by at0m-b0mb",
           font=F_REG(14), fill=MUTED)

    out = img.resize((W, H), Image.LANCZOS)
    out.save(OUT)
    print("saved", OUT, out.size)


if __name__ == "__main__":
    build()
