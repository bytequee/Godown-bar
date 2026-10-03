# pip install segno pillow opencv-python
"""
Print-ready QR code for the Godown Bar menu link.

Usage:
    python generate_qr.py https://lucent-blini-475f77.netlify.app/
    python generate_qr.py https://lucent-blini-475f77.netlify.app/ --logo Godown.jpeg

Writes into ./output/ :
    menu-qr.svg        vector, for print (scales to any size)
    menu-qr.png        >= 1200 px, for WhatsApp
    menu-qr-logo.png   same QR with the logo in the centre (only with --logo)
"""

import argparse
import io
import math
import sys
from pathlib import Path

import cv2
import numpy as np
import segno
from PIL import Image, ImageDraw

# --- settings ---------------------------------------------------------------
BORDER = 4           # quiet zone in modules - never crop this
DARK = "#000000"     # max contrast, scanners are happy
LIGHT = "#FFFFFF"
SHARE_PX = 1200      # minimum width of the WhatsApp PNG
LOGO_PX = 1600       # bigger, so the centre logo stays sharp
LOGO_RATIO = 0.18    # logo width vs QR width (keep it at or below 0.20)
PRINT_MM = 55        # printed width of the SVG in mm (table-tent size, edit as needed)

OUT = Path(__file__).resolve().parent / "output"


def write_svg(qr, path):
    """Vector version for print - scales to any size."""
    modules = qr.symbol_size(scale=1, border=BORDER)[0]
    # give it a real physical size, so it does not land in Word as a 37px stamp
    # light is set explicitly, otherwise the SVG background stays transparent
    qr.save(path, kind="svg", scale=PRINT_MM / modules, border=BORDER,
            dark=DARK, light=LIGHT, unit="mm")


def write_png(qr, path, min_px):
    """Raster version, at least min_px pixels wide."""
    modules = qr.symbol_size(scale=1, border=BORDER)[0]
    scale = max(1, math.ceil(min_px / modules))
    qr.save(path, kind="png", scale=scale, border=BORDER, dark=DARK, light=LIGHT)
    return scale


def write_logo_png(qr, logo_path, path):
    """Same QR, with the logo centred on a small white rounded square."""
    modules = qr.symbol_size(scale=1, border=BORDER)[0]
    scale = max(1, math.ceil(LOGO_PX / modules))

    # render to memory first, no temp file to clean up
    buf = io.BytesIO()
    qr.save(buf, kind="png", scale=scale, border=BORDER, dark=DARK, light=LIGHT)
    buf.seek(0)
    qr_img = Image.open(buf).convert("RGB")

    side = qr_img.width
    logo = Image.open(logo_path).convert("RGB")

    # logo is LOGO_RATIO of the QR width, aspect ratio kept
    logo_w = int(side * LOGO_RATIO)
    logo_h = max(1, round(logo_w * logo.height / logo.width))
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)

    pad = max(4, int(logo_w * 0.12))       # a few px of clean white around it
    plate = max(logo_w, logo_h) + 2 * pad
    radius = max(4, pad // 2)

    # the white plate goes down first, so the modules under it stay clean
    plate_img = Image.new("RGB", (plate, plate), LIGHT)
    ImageDraw.Draw(plate_img).rounded_rectangle(
        (0, 0, plate - 1, plate - 1), radius=radius, fill=LIGHT
    )

    # the logo is white line art on black, so keep the black as a rounded badge
    mask = Image.new("L", logo.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, logo_w - 1, logo_h - 1), radius=radius, fill=255
    )
    plate_img.paste(logo, ((plate - logo_w) // 2, (plate - logo_h) // 2), mask)

    qr_img.paste(plate_img, ((side - plate) // 2, (side - plate) // 2))
    qr_img.save(path)


def verify(path, expected):
    """Decode with OpenCV and check it matches the URL we encoded."""
    # np.fromfile + imdecode, so folder names with non-ascii chars still work
    img = cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return False, "could not read the image"

    det = cv2.QRCodeDetector()
    data, _, _ = det.detectAndDecode(img)
    if not data:                     # logo QRs sometimes need the second pass
        try:
            data, _ = det.detectAndDecodeCurved(img)
        except cv2.error:
            data = ""

    if data == expected:
        return True, data
    return False, data or "nothing decoded"


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_qr.py URL [--logo LOGO_FILE]")
        print("Example: python generate_qr.py https://lucent-blini-475f77.netlify.app/ --logo Godown.jpeg")
        sys.exit(1)

    ap = argparse.ArgumentParser(description="Print-ready QR code for the menu link.")
    ap.add_argument("url", help="menu URL, encoded straight into the QR")
    ap.add_argument("--logo", help="optional image placed in the centre of the QR")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)

    # static QR: the URL goes straight into the code, no redirect or tracking
    qr = segno.make(args.url, error="h")

    svg = OUT / "menu-qr.svg"
    png = OUT / "menu-qr.png"
    write_svg(qr, svg)
    write_png(qr, png, SHARE_PX)
    files = [png]

    if args.logo:
        logo_src = Path(args.logo)
        if not logo_src.is_file():
            print(f"FAIL  logo file not found: {logo_src}")
            sys.exit(1)
        logo_png = OUT / "menu-qr-logo.png"
        write_logo_png(qr, logo_src, logo_png)
        files.append(logo_png)

    print()
    all_ok = True
    for f in files:
        ok, detail = verify(f, args.url)
        all_ok = all_ok and ok
        print(f"{'PASS' if ok else 'FAIL'}  {f.name}  ->  {detail}")

    if len(files) > 1 and not all_ok:
        print("\nLogo version would not scan. Reduce the logo: set LOGO_RATIO = 0.15 or lower.")

    print("\nFiles:")
    for f in [svg] + files:
        print("  " + str(f.resolve()))
    print("\nTest-scan the printed version on 2-3 phones before handing over.")


if __name__ == "__main__":
    main()