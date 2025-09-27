#!/usr/bin/env python3
from gpiozero import Button
from signal import pause

# Replace 13 with the GPIO number for your working button
BTN = Button(13, pull_up=True, bounce_time=0.2)

counter = 0

def bump():
    global counter
    counter += 1
    print(f"Counter = {counter}")

BTN.when_pressed = bump

print("Press the button to bump the counter. Ctrl+C to exit.")
pause()
