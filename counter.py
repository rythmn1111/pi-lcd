#!/usr/bin/env python3
# Simple counter with button on Waveshare 1.44" LCD HAT
# Press the button to increment the counter

import time
import RPi.GPIO as GPIO
from lcd144 import LCD144

# Button configuration
BUTTON_PIN = 18  # Common pin for Waveshare 1.44" HAT button
DEBOUNCE_TIME = 0.2  # Prevent multiple triggers from single press

class ButtonCounter:
    def __init__(self):
        # Initialize LCD
        self.lcd = LCD144(
            rotation=0,
            bgr=True,
            invert=False,
            spi_hz=1_000_000
        )
        
        # Initialize button
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, 
                             callback=self.button_pressed, 
                             bouncetime=int(DEBOUNCE_TIME * 1000))
        
        # Counter state
        self.count = 0
        self.last_press_time = 0
        
        print("Counter started! Press the button to increment.")
        print("Press Ctrl+C to exit.")
        
    def button_pressed(self, channel):
        """Called when button is pressed"""
        current_time = time.time()
        
        # Debounce: ignore if pressed too recently
        if current_time - self.last_press_time < DEBOUNCE_TIME:
            return
            
        self.last_press_time = current_time
        self.count += 1
        print(f"Button pressed! Count: {self.count}")
        self.update_display()
    
    def update_display(self):
        """Update the LCD display with current count"""
        # Clear display with black background
        self.lcd.show_color(0, 0, 0)  # Black background
        time.sleep(0.1)
        
        # Show count in white
        self.lcd.show_color(255, 255, 255)  # White for visibility
        time.sleep(0.1)
        
        # Create a simple text display (we'll use colored rectangles as a visual counter)
        # For now, just show the count as a pattern
        self.show_count_pattern()
    
    def show_count_pattern(self):
        """Show count as a visual pattern"""
        # Create a simple pattern based on count
        # We'll use different colors for different count ranges
        
        if self.count == 0:
            # Black (no count yet)
            self.lcd.show_color(0, 0, 0)
        elif self.count <= 5:
            # Red for 1-5
            self.lcd.show_color(255, 0, 0)
        elif self.count <= 10:
            # Green for 6-10
            self.lcd.show_color(0, 255, 0)
        elif self.count <= 20:
            # Blue for 11-20
            self.lcd.show_color(0, 0, 255)
        else:
            # White for 20+
            self.lcd.show_color(255, 255, 255)
    
    def run(self):
        """Main loop"""
        try:
            # Initial display
            self.update_display()
            
            # Keep running until interrupted
            while True:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print(f"\nFinal count: {self.count}")
            print("Goodbye!")
        finally:
            # Cleanup
            GPIO.cleanup()
            self.lcd.show_color(0, 0, 0)  # Turn off display

if __name__ == "__main__":
    counter = ButtonCounter()
    counter.run()
