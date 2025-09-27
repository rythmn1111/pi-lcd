#!/usr/bin/env python3
# Display a JPEG on Waveshare 1.44" ST7735S (Pi Zero 2 W)
# - Tries hardware BGR mode; falls back to software R/B swap if needed
# - Handles EXIF orientation
# - Simple "fit" resize preserving aspect ratio

import argparse
from pathlib import Path
from PIL import Image, ImageOps, ImageCms, ExifTags
import ST7735

# ==== Default GPIOs for Waveshare 1.44" HAT (adjust if yours differ) ====
DC_PIN  = 25
RST_PIN = 27
BL_PIN  = 24       # set to None if your backlight isn't wired
PORT    = 0        # SPI0
CS      = 0        # CE0 => /dev/spidev0.0
WIDTH   = 128
HEIGHT  = 128
SPI_HZ  = 8_000_000

def load_jpeg(path: Path, w: int, h: int) -> Image.Image:
    """Open JPEG, honor EXIF orientation, convert to RGB, and letterbox-fit to (w,h)."""
    img = Image.open(path)

    # Auto-apply EXIF orientation if present
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    # Ensure RGB (handles JPEG in CMYK/other color spaces)
    if img.mode != "RGB":
        try:
            img = img.convert("RGB")
        except Exception:
            # In rare CMYK cases, force via ImageCms if available
            try:
                srgb = ImageCms.createProfile("sRGB")
                img = ImageCms.profileToProfile(img, img.info.get("icc_profile"), srgb, outputMode="RGB")
            except Exception:
                img = img.convert("RGB")

    # Fit with aspect ratio, pad with black if needed
    img = ImageOps.contain(img, (w, h))  # preserve aspect
    canvas = Image.new("RGB", (w, h), (0, 0, 0))
    x = (w - img.width) // 2
    y = (h - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas

def main():
    p = argparse.ArgumentParser(description="Show a JPEG on Waveshare 1.44\" ST7735S")
    p.add_argument("image", nargs="?", default="image.jpg", help="Path to a JPEG (default: image.jpg)")
    p.add_argument("--rotation", type=int, choices=(0, 90, 180, 270), default=0, help="Display rotation")
    p.add_argument("--speed", type=int, default=SPI_HZ, help="SPI speed (Hz)")
    p.add_argument("--color-mode", choices=("auto", "rgb", "bgr", "invert"), default="auto", 
                   help="Color mode: auto (try different modes), rgb, bgr, or invert")
    args = p.parse_args()

    img_path = Path(args.image)
    if not img_path.exists():
        raise SystemExit(f"Image not found: {img_path}")

    # Handle color mode based on user preference
    if args.color_mode == "auto":
        # Try different color modes to fix inversion
        # Method 1: Try with bgr=False (RGB mode)
        try:
            disp = ST7735.ST7735(
                port=PORT, cs=CS, dc=DC_PIN, rst=RST_PIN, backlight=BL_PIN,
                width=WIDTH, height=HEIGHT, rotation=args.rotation,
                spi_speed_hz=args.speed, bgr=False  # Try RGB mode first
            )
            color_mode = "rgb"
        except TypeError:
            # Older driver without `bgr` kwarg - try default
            try:
                disp = ST7735.ST7735(
                    port=PORT, cs=CS, dc=DC_PIN, rst=RST_PIN, backlight=BL_PIN,
                    width=WIDTH, height=HEIGHT, rotation=args.rotation,
                    spi_speed_hz=args.speed
                )
                color_mode = "default"
            except:
                # Last resort: try with bgr=True
                disp = ST7735.ST7735(
                    port=PORT, cs=CS, dc=DC_PIN, rst=RST_PIN, backlight=BL_PIN,
                    width=WIDTH, height=HEIGHT, rotation=args.rotation,
                    spi_speed_hz=args.speed, bgr=True
                )
                color_mode = "bgr"
    else:
        # Use specified color mode
        if args.color_mode == "rgb":
            disp = ST7735.ST7735(
                port=PORT, cs=CS, dc=DC_PIN, rst=RST_PIN, backlight=BL_PIN,
                width=WIDTH, height=HEIGHT, rotation=args.rotation,
                spi_speed_hz=args.speed, bgr=False
            )
            color_mode = "rgb"
        elif args.color_mode == "bgr":
            disp = ST7735.ST7735(
                port=PORT, cs=CS, dc=DC_PIN, rst=RST_PIN, backlight=BL_PIN,
                width=WIDTH, height=HEIGHT, rotation=args.rotation,
                spi_speed_hz=args.speed, bgr=True
            )
            color_mode = "bgr"
        else:  # invert mode
            disp = ST7735.ST7735(
                port=PORT, cs=CS, dc=DC_PIN, rst=RST_PIN, backlight=BL_PIN,
                width=WIDTH, height=HEIGHT, rotation=args.rotation,
                spi_speed_hz=args.speed
            )
            color_mode = "invert"

    disp.begin()

    frame = load_jpeg(img_path, WIDTH, HEIGHT)

    # Apply color correction based on the mode
    if color_mode == "bgr":
        # For BGR mode, swap R and B channels
        r, g, b = frame.split()
        frame = Image.merge("RGB", (b, g, r))
    elif color_mode == "rgb":
        # For RGB mode, keep as is
        pass
    elif color_mode == "invert":
        # Invert colors to fix inversion
        frame = ImageOps.invert(frame)
    else:
        # For default mode, try inverting colors to fix the issue
        frame = ImageOps.invert(frame)

    disp.display(frame)  # stays on screen until you draw again

if __name__ == "__main__":
    main()
