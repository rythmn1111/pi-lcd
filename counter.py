#!/usr/bin/env python3
import time
from PIL import Image
from st7735 import ST7735

# ==== LCD config (your known working values) ====
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

# ==== Colors to test ====
colors = [
    ("Red",   (255,   0,   0)),
    ("Green", (  0, 255,   0)),
    ("Blue",  (  0,   0, 255)),
    ("White", (255, 255, 255)),
    ("Black", (  0,   0,   0)),
]

for name, rgb in colors:
    print(f"Showing {name}")
    img = Image.new("RGB", (WIDTH, HEIGHT), rgb)
    disp.display(img)
    time.sleep(2)

print("Done.")
