#!/usr/bin/env python3

"""
tm2create.py form the TM2 Toolkit
Copyright (C) 2026 CosmicScale

<https://github.com/CosmicScale/TM2Toolkit>

SPDX-License-Identifier: GPL-3.0-or-later

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import struct
import os
from PIL import Image

# ------------------------------
# Hardcoded GS TEX registers (must remain fixed)
# ------------------------------
GS_TEX0 = bytes([0x00, 0x00, 0x30, 0x21, 0x02, 0x00, 0x00, 0x00])

# ------------------------------
# TIM2 file header builder
# ------------------------------
def build_tim2_file_header():
    header = bytearray(0x10)
    header[0:4] = b"TIM2"                   # Magic
    header[4] = 4                           # Version
    header[5] = 0                           # Format
    struct.pack_into("<H", header, 6, 1)    # Picture count
    return header

# ------------------------------
# TIM2 picture header builder
# ------------------------------
def build_tim2_picture_header(image_size, clut_size, width, height):
    header = bytearray(0x30)

    # Total picture size = header + image + palette
    total_size = 0x30 + image_size + clut_size
    struct.pack_into("<I", header, 0x00, total_size)  # Total size
    struct.pack_into("<I", header, 0x04, clut_size)   # CLUT size
    struct.pack_into("<I", header, 0x08, image_size)  # Image size
    struct.pack_into("<H", header, 0x0C, 0x30)        # Header size
    struct.pack_into("<H", header, 0x0E, 256)         # CLUT color count
    header[0x10] = 0                                  # Picture format
    header[0x11] = 1                                  # Mipmap count
    header[0x12] = 3                                  # CLUT color type (RGBA8888)
    header[0x13] = 5                                  # Image color type (8-bit indexed)
    struct.pack_into("<H", header, 0x14, width)       # Width
    struct.pack_into("<H", header, 0x16, height)      # Height

    # Determine GS_TEX1 based on texture size
    first_byte = 0x6C if (width, height) == (256, 256) else 0x60
    GS_TEX1 = bytes([first_byte, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    header[0x18:0x20] = GS_TEX0
    header[0x20:0x28] = GS_TEX1

    # Flags and CLUT registers left zero (0x28-0x2F)
    return header

# ------------------------------
# Palette swizzle (PS2-specific)
# ------------------------------
def swizzle_palette_256(pal):
    result = [None] * 256
    for block in range(8):
        base = block * 32
        block_colors = pal[base:base + 32]
        # Fill missing colors with black if palette is short
        while len(block_colors) < 32:
            block_colors.append((0, 0, 0))
        result[base + 0:base + 8] = block_colors[0:8]
        result[base + 8:base + 16] = block_colors[16:24]
        result[base + 16:base + 24] = block_colors[8:16]
        result[base + 24:base + 32] = block_colors[24:32]
    return result

# ------------------------------
# Apply alpha channel
# ------------------------------
def apply_palette_alpha(palette, alpha_value=128):
    return [(r, g, b, alpha_value) for r, g, b in palette]

# ------------------------------
# PNG to TIM2
# ------------------------------
def png_to_tm2(png_path):
    if not os.path.isfile(png_path):
        print(f"Error: Input file '{png_path}' does not exist or is not a file.")
        sys.exit(1)
    if not os.access(png_path, os.R_OK):
        print(f"Error: Input file '{png_path}' cannot be read (permission denied?).")
        sys.exit(1)

    # Load image with alpha
    with Image.open(png_path) as img:
        img = img.convert("RGBA")
        width, height = img.size

        # Separate RGB for palette generation
        rgb_img = img.convert("RGB")

        # Build palette using MEDIANCUT
        pal_base = rgb_img.quantize(
            colors=256,
            method=Image.MEDIANCUT,
            dither=Image.FLOYDSTEINBERG
        )

        # Apply palette to image
        pal_img = rgb_img.quantize(
            palette=pal_base,
            dither=Image.FLOYDSTEINBERG
        )

        # Extract RGB palette
        raw_palette = pal_img.getpalette()[:768]
        palette_rgb = [(raw_palette[i], raw_palette[i+1], raw_palette[i+2])
                       for i in range(0, len(raw_palette), 3)]

        # Get image indices
        image_indices = bytearray(pal_img.getdata())

        # Map palette index → alpha (halve original)
        pixels = list(img.getdata())
        palette_rgba = []
        for i in range(256):
            try:
                idx = image_indices.index(i)
                a = pixels[idx][3] // 2  # halve alpha
            except ValueError:
                a = 0
            palette_rgba.append((*palette_rgb[i], a))

    IMAGE_SIZE = len(image_indices)

    # Swizzle palette
    swizzled_rgba = swizzle_palette_256(palette_rgba)

    palette_bytes = b''.join(struct.pack("<BBBB", r, g, b, a) for r, g, b, a in swizzled_rgba)

    # Build headers
    file_header = build_tim2_file_header()
    picture_header = build_tim2_picture_header(
        IMAGE_SIZE,
        len(palette_bytes),
        width,
        height
    )

    # Combine all parts
    tim2_data = file_header + picture_header + image_indices + palette_bytes

    # Save TM2
    base_name = os.path.splitext(os.path.basename(png_path))[0]
    output_tm2_path = os.path.join(os.getcwd(), base_name + ".tm2")
    with open(output_tm2_path, "wb") as f:
        f.write(tim2_data)

    print(f"[+] Created PS2-correct TIM2: {output_tm2_path} ({width}x{height})")

# ------------------------------
# Main entry
# ------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <input.png>")
        sys.exit(1)

    png_to_tm2(sys.argv[1])