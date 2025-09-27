#!/usr/bin/env python3
# Manual GPIO Testing Program
# Tests common button pins and reports which one changes when pressed

import subprocess
import time

# Common button pins for Waveshare HATs
BUTTON_PINS = [18, 19, 21, 20, 16, 12, 7, 8, 25, 23, 24, 26]

def run_command(cmd):
    """Run a shell command and return the output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def test_gpio_pin(pin):
    """Test a specific GPIO pin for button activity"""
    print(f"\n🔍 Testing GPIO {pin}...")
    print("-" * 30)
    
    # Set pin as input
    run_command(f"raspi-gpio set {pin} ip")
    time.sleep(0.1)
    
    # Get initial state
    initial_output = run_command(f"raspi-gpio get {pin}")
    print(f"Initial state: {initial_output}")
    
    # Extract level value
    initial_level = None
    if "level=1" in initial_output:
        initial_level = 1
    elif "level=0" in initial_output:
        initial_level = 0
    
    if initial_level is None:
        print(f"❌ Could not read GPIO {pin} state")
        return False
    
    print(f"📊 Initial level: {initial_level}")
    print("⏰ Press your button now! (5 seconds)...")
    
    # Monitor for changes
    start_time = time.time()
    while time.time() - start_time < 5:
        current_output = run_command(f"raspi-gpio get {pin}")
        current_level = None
        
        if "level=1" in current_output:
            current_level = 1
        elif "level=0" in current_output:
            current_level = 0
        
        if current_level is not None and current_level != initial_level:
            print(f"✅ GPIO {pin} changed from {initial_level} to {current_level}!")
            print(f"🎯 FOUND! Button is on GPIO {pin}")
            return True
        
        time.sleep(0.1)
    
    print(f"❌ No change detected on GPIO {pin}")
    return False

def main():
    print("🔍 Manual GPIO Button Tester")
    print("=" * 50)
    print("This program will test common button pins.")
    print("Press your button when prompted for each pin.")
    print("=" * 50)
    
    found_pins = []
    
    for pin in BUTTON_PINS:
        if test_gpio_pin(pin):
            found_pins.append(pin)
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print("📋 RESULTS:")
    if found_pins:
        print(f"🎉 Found button(s) on GPIO: {found_pins}")
        print(f"✅ Use GPIO {found_pins[0]} in your counter code!")
        print(f"📝 Update BUTTON_PIN = {found_pins[0]} in counter.py")
    else:
        print("❌ No button detected on common pins.")
        print("💡 Try checking your HAT documentation.")
        print("💡 Or the button might be on a different pin.")
    
    print("\n🔧 To test a specific pin manually:")
    print("   raspi-gpio set 18 ip")
    print("   raspi-gpio get 18")
    print("   # Press button")
    print("   raspi-gpio get 18")

if __name__ == "__main__":
    main()
