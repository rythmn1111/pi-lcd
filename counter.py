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
        
        # Initialize button with error handling
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            # Try to add event detection
            try:
                GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, 
                                     callback=self.button_pressed, 
                                     bouncetime=int(DEBOUNCE_TIME * 1000))
                self.use_interrupt = True
                print(f"Button configured on GPIO {BUTTON_PIN} (interrupt mode)")
            except RuntimeError:
                print(f"Interrupt mode failed on GPIO {BUTTON_PIN}, using polling mode")
                self.use_interrupt = False
                
        except Exception as e:
            print(f"GPIO setup failed: {e}")
            print("Trying alternative GPIO pins...")
            self.try_alternative_pins()
        
        # Counter state
        self.count = 0
        self.last_press_time = 0
        self.last_button_state = True  # For polling mode
        
        print("Counter started! Press the button to increment.")
        print("Press Ctrl+C to exit.")
    
    def try_alternative_pins(self):
        """Try alternative GPIO pins for the button"""
        alternative_pins = [19, 21, 20, 16, 12, 7, 8, 25]
        
        for pin in alternative_pins:
            try:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                global BUTTON_PIN
                BUTTON_PIN = pin
                self.use_interrupt = True
                GPIO.add_event_detect(pin, GPIO.FALLING, 
                                     callback=self.button_pressed, 
                                     bouncetime=int(DEBOUNCE_TIME * 1000))
                print(f"Button found on GPIO {pin}!")
                return
            except:
                continue
        
        print("No working button pin found, using polling mode")
        self.use_interrupt = False
        
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
    
    def check_button_polling(self):
        """Check button state in polling mode"""
        if not self.use_interrupt:
            current_state = GPIO.input(BUTTON_PIN)
            # Button pressed when state changes from HIGH to LOW
            if self.last_button_state and not current_state:
                self.button_pressed(None)
            self.last_button_state = current_state
    
    def run(self):
        """Main loop"""
        try:
            # Initial display
            self.update_display()
            
            # Keep running until interrupted
            while True:
                if not self.use_interrupt:
                    self.check_button_polling()
                time.sleep(0.01)  # Check more frequently in polling mode
                
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
