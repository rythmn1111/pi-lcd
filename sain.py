#!/usr/bin/env python3
from st7735 import ST7735
from PIL import Image

disp = ST7735(
    port=0, cs=0, dc=25, rst=27, backlight=24,
    width=128, height=128, rotation=0,
    bgr=True, invert=False, spi_speed_hz=500000,
    offset_left=2, offset_top=3
)
disp.begin()

img = Image.new("RGB", (128,128), (255,0,0))  # red
disp.display(img)
