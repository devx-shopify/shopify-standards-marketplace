#!/usr/bin/env python3
"""Render the Excalidraw elements JSON used in the chat into a PNG.

Needs Pillow (pip install pillow). Draws the same boxes, labels, colors and
arrows as the chat diagram, in a clean style (not the hand-drawn look), so the
picture in the Doc matches what the user saw.

Supported elements: rectangle, ellipse, diamond (drawn as box), text, arrow,
label on shapes and arrows. cameraUpdate, delete and restoreCheckpoint are
ignored.

Usage:
    python render_diagram.py elements.json out.png [--scale 1.0]

The PNG is saved as an 8-bit palette image to keep it small.
"""

import argparse
import json
import math

from PIL import Image, ImageDraw, ImageFont

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
]


def font(size):
    for p in FONT_PATHS:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def color(c, default):
    if not c or c == "transparent":
        return default
    return c


def text_block(draw, cx, cy, text, size, fill="#1e1e1e", bg=None):
    f = font(size)
    lines = text.split("\n")
    widths = [draw.textlength(l, font=f) for l in lines]
    lh = size * 1.25
    total = lh * len(lines)
    if bg:
        w = max(widths) + 8
        draw.rectangle([cx - w / 2, cy - total / 2 - 2, cx + w / 2, cy + total / 2 + 2], fill=bg)
    y = cy - total / 2
    for line, w in zip(lines, widths):
        draw.text((cx - w / 2, y), line, font=f, fill=fill)
        y += lh


def bounds(els):
    xs, ys = [], []
    for e in els:
        if e.get("type") not in ("rectangle", "ellipse", "diamond", "text", "arrow"):
            continue
        x, y = e["x"], e["y"]
        if e["type"] == "arrow":
            for dx, dy in e.get("points", [[0, 0]]):
                xs.append(x + dx)
                ys.append(y + dy)
        elif e["type"] == "text":
            size = e.get("fontSize", 20)
            xs += [x, x + len(e["text"]) * size * 0.6]
            ys += [y, y + size * 1.4]
        else:
            xs += [x, x + e["width"]]
            ys += [y, y + e["height"]]
    return min(xs), min(ys), max(xs), max(ys)


def render(els, scale=1.0, pad=30):
    els = [e for e in els if e.get("type") not in ("cameraUpdate", "delete", "restoreCheckpoint")]
    x0, y0, x1, y1 = bounds(els)
    W = int((x1 - x0 + 2 * pad) * scale)
    H = int((y1 - y0 + 2 * pad) * scale)
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    def P(x, y):
        return ((x - x0 + pad) * scale, (y - y0 + pad) * scale)

    for e in els:
        t = e["type"]
        stroke = color(e.get("strokeColor"), "#1e1e1e")
        sw = max(1, int(e.get("strokeWidth", 2) * scale))
        if t in ("rectangle", "diamond", "ellipse"):
            a = P(e["x"], e["y"])
            b = P(e["x"] + e["width"], e["y"] + e["height"])
            fill = color(e.get("backgroundColor"), None)
            if t == "ellipse":
                d.ellipse([a, b], fill=fill, outline=stroke, width=sw)
            else:
                r = int(12 * scale) if e.get("roundness") else 0
                d.rounded_rectangle([a, b], radius=r, fill=fill, outline=stroke, width=sw)
            lab = e.get("label")
            if lab:
                text_block(d, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, lab["text"],
                           int(lab.get("fontSize", 20) * scale))
        elif t == "text":
            size = int(e.get("fontSize", 20) * scale)
            d.text(P(e["x"], e["y"]), e["text"], font=font(size), fill=stroke)
        elif t == "arrow":
            pts = [P(e["x"] + dx, e["y"] + dy) for dx, dy in e["points"]]
            d.line(pts, fill=stroke, width=sw)
            if e.get("endArrowhead", "arrow"):
                (ax, ay), (bx, by) = pts[-2], pts[-1]
                ang = math.atan2(by - ay, bx - ax)
                L = 12 * scale
                for s in (0.45, -0.45):
                    d.line([(bx, by), (bx - L * math.cos(ang + s), by - L * math.sin(ang + s))],
                           fill=stroke, width=sw)
            lab = e.get("label")
            if lab:
                mx = sum(p[0] for p in pts[:2]) / 2
                my = sum(p[1] for p in pts[:2]) / 2
                text_block(d, mx, my, lab["text"], int(lab.get("fontSize", 16) * scale), bg="white")
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("elements")
    ap.add_argument("out")
    ap.add_argument("--scale", type=float, default=1.0)
    a = ap.parse_args()
    with open(a.elements, encoding="utf-8") as f:
        els = json.load(f)
    img = render(els, a.scale)
    img.convert("P", palette=Image.ADAPTIVE, colors=64).save(a.out, optimize=True)
    print(f"Wrote {a.out} ({img.width}x{img.height})")


if __name__ == "__main__":
    main()
