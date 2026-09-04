import serial
import re
from datetime import datetime

PORT = '/dev/ttyACM0'
BAUD = 115200

STATE_RE = re.compile(r"'([^']+)'.*Sending state ([0-9.]+)")

# State
breath_rate = 0.0
heart_rate  = 0.0

def is_breathing(breath_rate, heart_rate):
    breath_ok = 8 <= breath_rate <= 30
    heart_ok  = 40 <= heart_rate <= 150
    return breath_ok and heart_ok

def handle_reading(sensor, value):
    global breath_rate, heart_rate

    ts = datetime.now().strftime('%H:%M:%S')

    if 'heart rate' in sensor.lower():
        heart_rate = value
        print(f"[{ts}] Heart Rate:   {value:.0f} bpm")

    elif 'breath' in sensor.lower():
        breath_rate = value
        print(f"[{ts}] Breath Rate:  {value:.0f} breaths/min")

    elif 'illuminance' in sensor.lower():
        # Uncomment if you want illuminance logged
        # print(f"[{ts}] Illuminance:  {value:.1f} lx")
        return

    else:
        print(f"[{ts}] {sensor}: {value}")
        return

    # Print presence status after every heart rate or breath update
    ts = datetime.now().strftime('%H:%M:%S')
    if is_breathing(breath_rate, heart_rate):
        print(f"[{ts}] STATUS: Person detected, breathing normally")
    elif heart_rate > 0 and breath_rate == 0:
        print(f"[{ts}] STATUS: Heart rate detected but no breath signal — check distance/angle")
    else:
        print(f"[{ts}] STATUS: No one detected")


def main():
    print(f"Opening {PORT} at {BAUD} baud...")
    try:
        ser = serial.Serial(PORT, baudrate=BAUD, timeout=2)
    except serial.SerialException as e:
        print(f"ERROR: Could not open port: {e}")
        return

    print("Listening for MR60BHA2 data. Ctrl+C to stop.\n")

    try:
        while True:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
            except serial.SerialException as e:
                print(f"ERROR: Serial read failed: {e}")
                break

            if not line:
                continue

            m = STATE_RE.search(line)
            if m:
                sensor = m.group(1)
                value  = float(m.group(2))
                handle_reading(sensor, value)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        ser.close()
        print("Port closed.")


if __name__ == '__main__':
    main()
