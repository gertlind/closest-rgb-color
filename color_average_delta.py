#!/usr/bin/env python3
import sys
import math
import yaml
from pathlib import Path
from PIL import Image

DB_PATH = Path(__file__).parent / "data" / "materials"


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def hex_to_rgb(hex_color):
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 8:
        hex_color = hex_color[:6]
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def srgb_to_linear(c):
    c = c / 255
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def rgb_to_lab(rgb):
    r, g, b = [srgb_to_linear(c) for c in rgb]

    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505

    x /= 0.95047
    y /= 1.00000
    z /= 1.08883

    def f(t):
        if t > 0.008856:
            return t ** (1 / 3)
        return (7.787 * t) + (16 / 116)

    fx, fy, fz = f(x), f(y), f(z)

    L = (116 * fy) - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)

    return (L, a, b)


def delta_e(lab1, lab2):
    return math.sqrt(
        (lab1[0] - lab2[0]) ** 2 +
        (lab1[1] - lab2[1]) ** 2 +
        (lab1[2] - lab2[2]) ** 2
    )


def average_image_color(image_path):
    img = Image.open(image_path).convert("RGBA")
    img = img.resize((100, 100))

    # pixels = list(img.getdata())
    pixels = list(img.get_flattened_data())

    # Ignorera helt transparenta pixlar
    visible_pixels = [
        (r, g, b)
        for r, g, b, a in pixels
        if a > 0
    ]

    avg_rgb = tuple(
        round(sum(channel) / len(visible_pixels))
        for channel in zip(*visible_pixels)
    )

    return avg_rgb


def main():
    if len(sys.argv) < 2:
        print("Usage: python find_image_color_deltae.py <bild.png> [max_results]")
        sys.exit(1)

    image_path = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) >= 3 else 20

    avg_rgb = average_image_color(image_path)
    avg_lab = rgb_to_lab(avg_rgb)

    results = []

    for file in DB_PATH.glob("*/*.yaml"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception:
            continue

        if not data:
            continue

        color_hex = data.get("primary_color", {}).get("color_rgba")
        if not color_hex:
            continue

        try:
            db_rgb = hex_to_rgb(color_hex)
            db_lab = rgb_to_lab(db_rgb)
        except Exception:
            continue

        distance = delta_e(avg_lab, db_lab)

        results.append({
            "delta_e": distance,
            "brand": data.get("brand", {}).get("slug", ""),
            "name": data.get("name", ""),
            "type": data.get("type", ""),
            "color": color_hex,
            "url": data.get("url", ""),
            # "file": str(file)
        })

    results.sort(key=lambda x: x["delta_e"])

    print("Image average RGB:", avg_rgb)
    print("Image average HEX:", rgb_to_hex(avg_rgb))
    print()
    print("brand,name,type,color,delta_e,url,file")

    for r in results[:max_results]:
        print(
            f'{r["brand"]},'
            f'"{r["name"]}",'
            f'{r["type"]},'
            f'{r["color"]},'
            f'{round(r["delta_e"], 2)},'
            f'{r["url"]},'
            # f'{r["file"]}'
        )


if __name__ == "__main__":
    main()
