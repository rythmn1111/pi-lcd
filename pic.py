#!/usr/bin/env python3
# Display images/GIFs/WebP on Waveshare 1.44" ST7735S using LCD144 helper
# - Clean, simple interface
# - Handles EXIF orientation, color correction, cropping
# - Supports static images, GIFs, and WebP animations

import argparse
import time
from pathlib import Path
from PIL import Image, ImageOps, ImageCms, ExifTags

# Import the LCD144 helper class
try:
    from lcd144 import LCD144
except ImportError:
    print("LCD144 helper not found. Please install it first:")
    print("1. Create ~/libs/lcd144/ directory")
    print("2. Add lcd144.py with the LCD144 class")
    print("3. Run: cd ~/libs/lcd144 && pip3 install -e . --break-system-packages")
    exit(1)

# Note: Image loading is now handled by LCD144.show_image()

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

# Note: Test patterns and diagnostics are now handled by LCD144.show_color()

def main():
    p = argparse.ArgumentParser(description="Show images/GIFs/WebP on Waveshare 1.44\" ST7735S")
    p.add_argument("image", nargs="?", help="Path to an image, GIF, or WebP")
    p.add_argument("--rotation", type=int, choices=(0, 90, 180, 270), default=0, help="Display rotation")
    p.add_argument("--landscape", action="store_true", help="Force landscape mode (90 degree rotation)")
    p.add_argument("--speed", type=int, default=1_000_000, help="SPI speed (Hz)")
    p.add_argument("--color-mode", choices=("rgb", "bgr", "invert"), default="bgr", 
                   help="Color mode: rgb, bgr, or invert")
    p.add_argument("--loop", type=int, default=0, help="Number of times to loop animated image (0 = infinite)")
    p.add_argument("--fps", type=float, default=10.0, help="Override animated image frame rate (FPS, default: 10)")
    p.add_argument("--crop-right", type=int, default=0, help="Crop N pixels from right edge to avoid noise (default: 0)")
    p.add_argument("--test", action="store_true", help="Show test pattern instead of image")
    p.add_argument("--diagnose", action="store_true", help="Run comprehensive hardware diagnostics")
    args = p.parse_args()

    # Handle missing image argument
    if not args.image:
        if args.test:
            # Test mode doesn't need an image
            img_path = None
        else:
            # Try to find any image file in current directory
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            found_image = None
            for ext in image_extensions:
                for pattern in [f"*{ext}", f"*{ext.upper()}"]:
                    import glob
                    files = glob.glob(pattern)
                    if files:
                        found_image = files[0]
                        break
                if found_image:
                    break
            
            if found_image:
                img_path = Path(found_image)
                print(f"Using found image: {img_path}")
            else:
                print("No image specified and no image files found in current directory.")
                print("Usage: python pic.py <image_file> or python pic.py --test")
                print("Supported formats: JPG, PNG, GIF, WebP")
                return
    else:
        img_path = Path(args.image)
        if not img_path.exists():
            raise SystemExit(f"Image not found: {img_path}")

# Note: Display initialization is now handled by LCD144 class

    # Handle landscape mode
    if args.landscape:
        args.rotation = 90  # Force 90 degree rotation for landscape
    
    # Initialize LCD144 with settings
    print(f"Initializing LCD144 with rotation={args.rotation}, speed={args.speed}Hz, crop={args.crop_right}px")
    
    lcd = LCD144(
        rotation=args.rotation,
        bgr=(args.color_mode == "bgr"),
        invert=(args.color_mode == "invert"),
        spi_hz=args.speed
    )
    
    # Show test pattern if requested
    if args.test:
        print("Showing test pattern...")
        lcd.show_color(255, 0, 0, mask_right_px=args.crop_right)  # Red
        time.sleep(1)
        lcd.show_color(0, 255, 0, mask_right_px=args.crop_right)  # Green
        time.sleep(1)
        lcd.show_color(0, 0, 255, mask_right_px=args.crop_right)  # Blue
        time.sleep(1)
        lcd.show_color(255, 255, 255, mask_right_px=args.crop_right)  # White
        print("Test pattern complete. Check for:")
        print("- Red, Green, Blue, White colors")
        print("- Any vertical lines or color bleeding")
        return
    
    # Check if it's an animated format (GIF or WebP)
    is_animated = img_path and img_path.suffix.lower() in ['.gif', '.webp']
    
    if is_animated:
        # Handle animated GIF or WebP
        frames, durations = load_animated_frames(img_path, 128, 128)
        
        if not frames:
            raise SystemExit("No frames found in animated image")
        
        print(f"Loaded animated image with {len(frames)} frames")
        
        # Override frame durations with specified FPS
        frame_duration = 1000 / args.fps  # Convert FPS to milliseconds
        durations = [frame_duration] * len(frames)
        print(f"Using {args.fps} FPS ({frame_duration:.1f}ms per frame)")
        
        loop_count = 0
        while True:
            for i, (frame, duration) in enumerate(zip(frames, durations)):
                # Apply cropping to the frame
                if args.crop_right > 0:
                    from PIL import ImageDraw
                    draw = ImageDraw.Draw(frame)
                    draw.rectangle(
                        [128 - args.crop_right, 0, 127, 127],
                        fill=(0, 0, 0)
                    )
                
                # Display the frame directly
                lcd.disp.display(frame)
                
                # Wait for frame duration (convert ms to seconds)
                time.sleep(duration / 1000.0)
            
            loop_count += 1
            if args.loop > 0 and loop_count >= args.loop:
                break
                
    else:
        # Handle static image - use LCD144's built-in image display
        print(f"Displaying image: {img_path}")
        lcd.show_image(str(img_path), mask_right_px=args.crop_right)

if __name__ == "__main__":
    main()
