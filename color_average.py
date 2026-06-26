#!/usr/bin/env python3
import sys
from PIL import Image

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)

if len(sys.argv) != 2:
    print("Usage: python average_image_color.py <bildfil>")
    sys.exit(1)

image_path = sys.argv[1]

img = Image.open(image_path).convert("RGB")

# Gör bilden mindre så beräkningen går snabbt
img = img.resize((100, 100))

pixels = list(img.getdata())

avg_rgb = tuple(
    round(sum(channel) / len(pixels))
    for channel in zip(*pixels)
)

print("Average RGB:", avg_rgb)
print("Average HEX:", rgb_to_hex(avg_rgb))
