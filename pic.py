import ST7735
from PIL import Image

# ==== Display setup ====
disp = ST7735.ST7735(
    port=0,
    cs=0,
    dc=25,      # your DC pin
    rst=27,     # your RST pin
    backlight=24,  # set to None if not wired
    width=128,
    height=128,
    rotation=0,
    spi_speed_hz=4000000
)
disp.begin()

# ==== Load and resize JPEG ====
img = Image.open("dum.jpeg").convert("RGB")
img = img.resize((128, 128))   # scale to fit LCD

# ==== Show it ====
disp.display(img)
