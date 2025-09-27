#!/usr/bin/env python3
# Display a JPEG on Waveshare 1.44" ST7735S (Pi Zero 2 W)
# - Tries hardware BGR mode; falls back to software R/B swap if needed
# - Handles EXIF orientation
# - Simple "fit" resize preserving aspect ratio

import argparse
import time
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

def load_image(path: Path, w: int, h: int) -> Image.Image:
    """Open image (JPEG/GIF), honor EXIF orientation, convert to RGB, and letterbox-fit to (w,h)."""
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

def load_animated_frames(path: Path, w: int, h: int) -> list:
    """Load all frames from an animated image (GIF/WebP) and prepare them for display."""
    frames = []
    durations = []
    
    with Image.open(path) as img:
        # Get frame count
        frame_count = getattr(img, 'n_frames', 1)
        
        for frame_idx in range(frame_count):
            img.seek(frame_idx)
            
            # Convert to RGB
            frame = img.convert("RGB")
            
            # Auto-apply EXIF orientation if present
            try:
                frame = ImageOps.exif_transpose(frame)
            except Exception:
                pass
            
            # Fit with aspect ratio, pad with black if needed
            frame = ImageOps.contain(frame, (w, h))
            canvas = Image.new("RGB", (w, h), (0, 0, 0))
            x = (w - frame.width) // 2
            y = (h - frame.height) // 2
            canvas.paste(frame, (x, y))
            
            frames.append(canvas)
            
            # Get frame duration (default to 100ms if not specified)
            duration = img.info.get('duration', 100)
            durations.append(duration)
    
    return frames, durations

def create_test_pattern(w: int, h: int) -> Image.Image:
    """Create a test pattern to help diagnose display issues."""
    img = Image.new("RGB", (w, h), (0, 0, 0))  # Start with black
    
    # Draw colored rectangles to test display
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    
    # Red rectangle (top-left)
    draw.rectangle([0, 0, w//2, h//2], fill=(255, 0, 0))
    
    # Green rectangle (top-right)
    draw.rectangle([w//2, 0, w, h//2], fill=(0, 255, 0))
    
    # Blue rectangle (bottom-left)
    draw.rectangle([0, h//2, w//2, h], fill=(0, 0, 255))
    
    # White rectangle (bottom-right)
    draw.rectangle([w//2, h//2, w, h], fill=(255, 255, 255))
    
    return img

def main():
    p = argparse.ArgumentParser(description="Show images/GIFs/WebP on Waveshare 1.44\" ST7735S")
    p.add_argument("image", nargs="?", default="image.jpg", help="Path to an image, GIF, or WebP (default: image.jpg)")
    p.add_argument("--rotation", type=int, choices=(0, 90, 180, 270), default=0, help="Display rotation")
    p.add_argument("--landscape", action="store_true", help="Force landscape mode (90 degree rotation)")
    p.add_argument("--speed", type=int, default=SPI_HZ, help="SPI speed (Hz)")
    p.add_argument("--color-mode", choices=("auto", "rgb", "bgr", "invert"), default="auto", 
                   help="Color mode: auto (try different modes), rgb, bgr, or invert")
    p.add_argument("--loop", type=int, default=0, help="Number of times to loop animated image (0 = infinite)")
    p.add_argument("--fps", type=float, default=None, help="Override animated image frame rate (FPS)")
    p.add_argument("--clear", action="store_true", help="Clear display before showing image")
    p.add_argument("--slow-spi", action="store_true", help="Use slower SPI speed to fix display issues")
    p.add_argument("--test", action="store_true", help="Show test pattern instead of image")
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

    # Handle landscape mode
    if args.landscape:
        args.rotation = 90  # Force 90 degree rotation for landscape
    
    # Handle slow SPI mode
    if args.slow_spi:
        args.speed = 1_000_000  # Use 1MHz instead of 8MHz
        print("Using slow SPI mode (1MHz) to fix display issues")
    
    # Clear display if requested
    if args.clear:
        print("Clearing display...")
        black_image = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        disp.display(black_image)
        time.sleep(0.1)  # Give it time to clear
    
    # Show test pattern if requested
    if args.test:
        print("Showing test pattern...")
        test_img = create_test_pattern(WIDTH, HEIGHT)
        
        # Apply color correction
        if color_mode == "bgr":
            r, g, b = test_img.split()
            test_img = Image.merge("RGB", (b, g, r))
        elif color_mode == "invert":
            test_img = ImageOps.invert(test_img)
        
        disp.display(test_img)
        print("Test pattern displayed. Check for:")
        print("- Red (top-left), Green (top-right), Blue (bottom-left), White (bottom-right)")
        print("- Any vertical lines or color bleeding")
        return
    
    # Check if it's an animated format (GIF or WebP)
    is_animated = img_path.suffix.lower() in ['.gif', '.webp']
    
    if is_animated:
        # Handle animated GIF or WebP
        frames, durations = load_animated_frames(img_path, WIDTH, HEIGHT)
        
        if not frames:
            raise SystemExit("No frames found in animated image")
        
        print(f"Loaded animated image with {len(frames)} frames")
        
        # Override frame durations if FPS is specified
        if args.fps:
            frame_duration = 1000 / args.fps  # Convert FPS to milliseconds
            durations = [frame_duration] * len(frames)
            print(f"Using {args.fps} FPS ({frame_duration:.1f}ms per frame)")
        
        loop_count = 0
        while True:
            for i, (frame, duration) in enumerate(zip(frames, durations)):
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
                
                disp.display(frame)
                
                # Wait for frame duration (convert ms to seconds)
                time.sleep(duration / 1000.0)
            
            loop_count += 1
            if args.loop > 0 and loop_count >= args.loop:
                break
                
    else:
        # Handle static image
        frame = load_image(img_path, WIDTH, HEIGHT)

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
