"""Generate collector.ico - the desktop shortcut icon (WO-UI-01 §11).

Kept as a script rather than committing a binary nobody can regenerate or
explain. Run it and you get the same file back:

    python make_icon.py

Standard library only - no Pillow, nothing to install. It writes PNG-compressed
ICO entries, which Windows has accepted since Vista.

The mark is the UI's own palette: a dark plate (#14171c) with a green ring and
centre (#46c17c), so the taskbar icon and the window read as the same program.
"""

import struct
import zlib
from pathlib import Path

BG = (0x14, 0x17, 0x1C, 0xFF)      # window background
FG = (0x46, 0xC1, 0x7C, 0xFF)      # the "collecting" green
DIM = (0x2D, 0x33, 0x3C, 0xFF)     # panel border


def draw(size):
    """Return RGBA rows for one square icon of the given size."""
    px = [[BG for _ in range(size)] for _ in range(size)]
    c = (size - 1) / 2.0

    r_out = size * 0.40      # outer ring
    r_in = size * 0.30       # inner edge of ring
    r_dot = size * 0.15      # centre dot
    edge = size * 0.02       # antialias band

    for y in range(size):
        for x in range(size):
            d = ((x - c) ** 2 + (y - c) ** 2) ** 0.5

            # centre dot
            if d <= r_dot:
                px[y][x] = FG
                continue
            # ring
            if r_in <= d <= r_out:
                px[y][x] = FG
                continue
            # soft edges so it does not look jagged at 16px
            if r_out < d <= r_out + edge or r_in - edge <= d < r_in:
                px[y][x] = DIM
                continue
    return px


def png_bytes(px):
    """Encode RGBA rows as a PNG."""
    size = len(px)
    raw = bytearray()
    for row in px:
        raw.append(0)  # filter type 0 (None)
        for r, g, b, a in row:
            raw += bytes((r, g, b, a))

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    sizes = [16, 32, 48, 64, 128, 256]
    images = [png_bytes(draw(s)) for s in sizes]

    header = struct.pack("<HHH", 0, 1, len(images))
    offset = len(header) + 16 * len(images)

    entries, blobs = b"", b""
    for s, img in zip(sizes, images):
        # 256 is stored as 0 in the ICO directory.
        dim = 0 if s == 256 else s
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(img), offset)
        offset += len(img)
        blobs += img

    out = Path(__file__).with_name("collector.ico")
    with open(out, "wb") as fh:          # binary mode takes no encoding
        fh.write(header + entries + blobs)

    print("wrote %s (%d bytes, %d sizes)" % (out, out.stat().st_size, len(sizes)))


if __name__ == "__main__":
    main()
