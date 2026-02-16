#!/usr/bin/env python3

"""
psm2tm2.py form the TM2 Toolkit
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

import struct
import sys
import os

def extract_tim2(psm_path, output_path=None):
    # Check if input file exists and is readable
    if not os.path.isfile(psm_path):
        print(f"Error: Input file '{psm_path}' does not exist or is not a file.")
        sys.exit(1)
    if not os.access(psm_path, os.R_OK):
        print(f"Error: Input file '{psm_path}' cannot be read (permission denied?).")
        sys.exit(1)

    with open(psm_path, "rb") as f:
        data = f.read()

    # Verify PS2S magic
    if data[0:4] != b"PS2S":
        raise ValueError("Not a PS2S container.")

    # Read thumbnail size (offset 0x40)
    thumb_size = struct.unpack_from("<I", data, 0x40)[0]

    # Read thumbnail offset (offset 0x44)
    thumb_offset = struct.unpack_from("<I", data, 0x44)[0]

    print(f"[+] Thumbnail offset : 0x{thumb_offset:X}")
    print(f"[+] Thumbnail size   : {thumb_size} bytes")

    # Basic sanity checks
    if thumb_offset + thumb_size > len(data):
        raise ValueError("Thumbnail extends beyond file size.")

    # Extract thumbnail
    thumb_data = data[thumb_offset:thumb_offset + thumb_size]

    # Verify TIM2 magic
    if thumb_data[0:4] != b"TIM2":
        raise ValueError("Extracted data is not TIM2.")

    # Output path defaults to input filename with .tm2 extension
    if output_path is None:
        output_path = os.path.splitext(os.path.basename(psm_path))[0] + ".tm2"

    with open(output_path, "wb") as f:
        f.write(thumb_data)

    print(f"[+] TIM2 extracted to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input_file.psm>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    extract_tim2(input_file, output_file)
