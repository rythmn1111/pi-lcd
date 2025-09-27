#!/usr/bin/env python3
from gpiozero import Button
from PIL import Image, ImageDraw, ImageFont
from st7735 import ST7735
from signal import pause

# ==== LCD config (tuned for Waveshare 1.44") ====
DC_PIN, RST_PIN, BL_PIN = 25, 27, 24
WIDTH, HEIGHT = 128, 128
OFFSET_LEFT, OFFSET_TOP = 2, 3
SPI_HZ = 2_000_000  # raise if stable
BGR, INVERT, ROTATION = True, False, 0

disp = ST7735(
    port=0, cs=0, dc=DC_PIN, rst=RST_PIN, backlight=BL_PIN,
    width=WIDTH, height=HEIGHT, rotation=ROTATION,
    bgr=BGR, invert=INVERT, spi_speed_hz=SPI_HZ,
    offset_left=OFFSET_LEFT, offset_top=OFFSET_TOP
)
disp.begin()

# ==== Button ====
BTN = Button(13, pull_up=True, bounce_time=0.2)  # BCM 13 = DOWN

# ==== Counter state ====
counter = 0

# ==== Font setup ====
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
except:
    font = ImageFont.load_default()

def update_display():
    """Draw current counter on screen."""
    img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    text = str(counter)
    tw, th = draw.textsize(text, font=font)
    x = (WIDTH - tw) // 2
    y = (HEIGHT - th) // 2
    draw.text((x, y), text, font=font, fill=(255, 255, 255))

    disp.display(img)

def bump():
    global counter
    counter += 1
    update_display()
    print(f"Counter = {counter}")

# First draw
update_display()

BTN.when_pressed = bump

print("Press button to increment counter. Ctrl+C to exit.")
pause()
