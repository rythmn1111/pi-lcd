#!/usr/bin/env python3
from gpiozero import Button
from signal import pause

# Active-low buttons with internal pull-ups
KEY1  = Button(6,  pull_up=True, bounce_time=0.05)
KEY2  = Button(19, pull_up=True, bounce_time=0.05)
KEY3  = Button(5,  pull_up=True, bounce_time=0.05)
UP    = Button(26, pull_up=True, bounce_time=0.05)
DOWN  = Button(13, pull_up=True, bounce_time=0.05)
LEFT  = Button(20, pull_up=True, bounce_time=0.05)
RIGHT = Button(16, pull_up=True, bounce_time=0.05)
PRESS = Button(21, pull_up=True, bounce_time=0.05)

def on(name):
    def _f():
        print(f"{name} pressed")
    return _f

for name, btn in {
    "KEY1":KEY1, "KEY2":KEY2, "KEY3":KEY3,
    "UP":UP, "DOWN":DOWN, "LEFT":LEFT, "RIGHT":RIGHT, "PRESS":PRESS
}.items():
    btn.when_pressed = on(name)

print("Press buttons/joystick... Ctrl+C to exit")
pause()
