#!/usr/bin/env python3
# GPIO Button Detector for Waveshare 1.44" LCD HAT
# This will help find which GPIO pin your button is connected to

import RPi.GPIO as GPIO
import time

# Common button pins for Waveshare HATs
BUTTON_PINS = [18, 19, 21, 20, 16, 12, 7, 8, 25, 23, 24, 25, 26]

def test_gpio_pin(pin):
    """Test a specific GPIO pin for button activity"""
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        print(f"Testing GPIO {pin}...")
        print("  Press the button now! (5 seconds)")
        
        initial_state = GPIO.input(pin)
        print(f"  Initial state: {initial_state}")
        
        # Monitor for 5 seconds
        start_time = time.time()
        while time.time() - start_time < 5:
            current_state = GPIO.input(pin)
            if current_state != initial_state:
                print(f"  ✅ GPIO {pin} changed from {initial_state} to {current_state}!")
                print(f"  🎯 FOUND! Button is on GPIO {pin}")
                return True
            time.sleep(0.01)
        
        print(f"  ❌ No change detected on GPIO {pin}")
        return False
        
    except Exception as e:
        print(f"  ❌ Error testing GPIO {pin}: {e}")
        return False
    finally:
        GPIO.cleanup()

def main():
    print("🔍 GPIO Button Detector")
    print("=" * 40)
    print("This will test common button pins.")
    print("Press your button when prompted!")
    print()
    
    found_pins = []
    
    for pin in BUTTON_PINS:
        if test_gpio_pin(pin):
            found_pins.append(pin)
        print()
        time.sleep(1)  # Brief pause between tests
    
    print("=" * 40)
    if found_pins:
        print(f"🎉 Found button(s) on GPIO: {found_pins}")
        print(f"Use GPIO {found_pins[0]} in your code!")
    else:
        print("❌ No button detected on common pins.")
        print("Try checking your HAT documentation for the button pin.")
        print("Or the button might be on a different pin not tested.")

if __name__ == "__main__":
    main()
