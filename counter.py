#!/usr/bin/env python3
from gpiozero import Button
from PIL import Image, ImageDraw, ImageFont
from st7735 import ST7735
from signal import pause

# ==== LCD config (your working params) ====
DC_PIN, RST_PIN, BL_PIN = 25, 27, 24
WIDTH, HEIGHT = 128, 128
OFFSET_LEFT, OFFSET_TOP = 2, 3
SPI_HZ = 2_000_000

disp = ST7735(
    port=0, cs=0, dc=DC_PIN, rst=RST_PIN, backlight=BL_PIN,
    width=WIDTH, height=HEIGHT, rotation=0,
    bgr=True, invert=False, spi_speed_hz=SPI_HZ,
    offset_left=OFFSET_LEFT, offset_top=OFFSET_TOP
)
disp.begin()

# ==== Button (your working one was GPIO13) ====
BTN = Button(13, pull_up=True, bounce_time=0.2)

counter = 0
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
except:
    font = ImageFont.load_default()

def update_display():
    img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))  # black background
    draw = ImageDraw.Draw(img)
    text = str(counter)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = (WIDTH - tw) // 2, (HEIGHT - th) // 2
    draw.text((x, y), text, font=font, fill=(255, 255, 255))
    disp.display(img)

def bump():
    global counter
    counter += 1
    update_display()
    print(f"Counter = {counter}")

# Draw initial 0
update_display()
BTN.when_pressed = bump

print("Press button to increment counter. Ctrl+C to exit.")
pause()
