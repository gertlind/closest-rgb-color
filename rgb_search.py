#!/usr/bin/env python3
import sys
import yaml
import math
from pathlib import Path

DB_PATH = Path("openprinttag-database/data/materials")


def hex_to_rgb(hex_color):
    hex_color = hex_color.strip().lstrip("#")

    # Tillåt #RRGGBB eller #RRGGBBAA
    if len(hex_color) == 8:
        hex_color = hex_color[:6]

    if len(hex_color) != 6:
        raise ValueError("Color value need to be. #ff0000 or #ff0000ff")

    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def color_distance(c1, c2):
    return math.sqrt(
        (c1[0] - c2[0]) ** 2 +
        (c1[1] - c2[1]) ** 2 +
        (c1[2] - c2[2]) ** 2
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: python find_color.py <hexcolor> [max_results]")
        print("Example: python find_color.py '#363331' 10")
        sys.exit(1)

    search_color = hex_to_rgb(sys.argv[1])
    max_results = int(sys.argv[2]) if len(sys.argv) >= 3 else 10

    results = []

    for file in DB_PATH.glob("*/*.yaml"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception:
            continue

        if not data:
            continue

        primary_color = data.get("primary_color", {})
        color_hex = primary_color.get("color_rgba")

        if not color_hex:
            continue

        try:
            material_color = hex_to_rgb(color_hex)
        except ValueError:
            continue

        distance = color_distance(search_color, material_color)

        #results.append({
        #    "distance": distance,
        #    "brand": data.get("brand", {}).get("slug", ""),
        #    "name": data.get("name", ""),
        #    "type": data.get("type", ""),
        #    "color": color_hex,
        #    "file": str(file)
        #})

        results.append({
            "distance": distance,
            "brand": data.get("brand", {}).get("slug", ""),
            "name": data.get("name", ""),
            "type": data.get("type", ""),
            "color": color_hex,
            "url": data.get("url", ""),
        #    "file": str(file)
        })

    results.sort(key=lambda x: x["distance"])

    #print("brand,name,type,color,distance,file")
    print("brand,name,type,color,distance,url")

    for r in results[:max_results]:
        print(
            #f'{r["brand"]},'
            #f'"{r["name"]}",'
            #f'{r["type"]},'
            #f'{r["color"]},'
            #f'{round(r["distance"], 2)},'
            #f'{r["file"]}'
            f'{r["brand"]},'
            f'"{r["name"]}",'
            f'{r["type"]},'
            f'{r["color"]},'
            f'{round(r["distance"], 2)},'
            f'{r["url"]}'
            #f'{r["file"]}'
        )


if __name__ == "__main__":
    main()
