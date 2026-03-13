#!/usr/bin/env python3

"""
tm2extract.py form the TM2 Toolkit
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
from PIL import Image
import os

def deswizzle_palette_256(pal):
    result = []
    for block in range(8):
        base = block * 32
        block_colors = pal[base:base + 32]
        result.extend(
            block_colors[0:8] +
            block_colors[16:24] +
            block_colors[8:16] +
            block_colors[24:32]
        )
    return result

def tm2_to_png(tm2_path, png_path, flatten_alpha=False):
    try:
        with open(tm2_path, "rb") as f:

            if f.read(4) != b"TIM2":
                raise ValueError("Not a TIM2 file")

            version, alignment, texture_count = struct.unpack("<BBH", f.read(4))
            f.seek(8, 1)

            if alignment != 0:
                f.seek(0x70, 1)

            header = f.read(0x30)
            total_size, palette_size, image_size, header_size = struct.unpack("<IIIH", header[:14])
            color_entries = struct.unpack("<H", header[14:16])[0]
            depth = header[19]
            width, height = struct.unpack("<HH", header[20:24])
            f.seek(header_size - 0x30, 1)

            image_data = f.read(image_size)
            palette_data = f.read(palette_size)
    except Exception as e:
        print(f"Error: Could not read input file '{tm2_path}': {e}")
        sys.exit(1)

    # Decode palette (RGBA)
    palette = [rgba for rgba in struct.iter_unpack("<BBBB", palette_data)]
    palette = deswizzle_palette_256(palette)

    if flatten_alpha:
        flat_palette = [c for rgba in palette for c in rgba[:3]]
        img = Image.frombytes("P", (width, height), image_data)
        img.putpalette(flat_palette[:768])
    else:
        img = Image.frombytes("P", (width, height), image_data)
        flat_palette = [c for rgba in palette for c in rgba[:3]]
        img.putpalette(flat_palette[:768])
        alpha = Image.new("L", (width, height))
        alpha.putdata([min(255, palette[p][3] * 2) for p in img.tobytes()])
        img = img.convert("RGBA")
        img.putalpha(alpha)

    img.save(png_path)
    print(f"Extracted {width}x{height} image to {png_path} (alpha={'ignored' if flatten_alpha else 'enabled'})")

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(f"Usage: {sys.argv[0]} [-f|--flatten] <input_file.tm2>")
        sys.exit(1)

    flatten_alpha = False
    input_file = None

    # Parse arguments
    if len(sys.argv) == 2:
        input_file = sys.argv[1]
    elif len(sys.argv) == 3:
        if sys.argv[1] in ("--flatten", "-f"):
            flatten_alpha = True
            input_file = sys.argv[2]
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print(f"Usage: {sys.argv[0]} [-f|--flatten] <input_file.tm2>")
            sys.exit(1)

    # Check if input file exists and is readable
    if not os.path.isfile(input_file):
        print(f"Error: Input file '{input_file}' does not exist or is not a file.")
        sys.exit(1)
    if not os.access(input_file, os.R_OK):
        print(f"Error: Input file '{input_file}' cannot be read (permission denied?).")
        sys.exit(1)

    output_file = os.path.splitext(os.path.basename(input_file))[0] + ".png"
    tm2_to_png(input_file, output_file, flatten_alpha)
