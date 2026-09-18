# Firmware

MicroPython source for the Team 15 meeting timer, targeting the Seeed Studio
XIAO ESP32-S3 running MicroPython v1.28.0.

## Files

| File | Purpose | Owner |
|---|---|---|
| `config.py` | Pin assignments, step sequence, presets, timing constants. Every other module imports from here. | Bharath |
| `stepper.py` | Wave-drive control of the 28BYJ-48 through the L293D H-bridge. | Tris |
| `leds.py` | Three-color LED output with PWM pulsing. | Deniz |
| `buttons.py` | Debounced switch input with short and long press detection. | Micky |
| `main.py` | Top-level state machine. Runs automatically at power-on. | Beatrice |

## Design notes

All four hardware modules are **non-blocking**. Nothing calls `time.sleep()`
inside normal operation. Instead each module exposes an `update()` or `poll()`
that is called every pass of the main loop and returns immediately. This is
what lets the hand move, the LED pulse, and the buttons respond at the same
time on a single core with no threads.

Pin numbers appear in `config.py` and nowhere else. If the wiring changes, that
is the only file that should need editing.

## Loading onto the board

1. Open Thonny and select **MicroPython (ESP32)** as the interpreter, with the
   XIAO's serial port.
2. Open each file and use **File > Save as... > MicroPython device** to copy it
   to the board. All five files go in the device root.
3. Reset the board. `main.py` runs automatically.

## Testing individual modules

`stepper.py`, `leds.py`, and `buttons.py` each have a standalone test block at
the bottom. Open one in Thonny and press Run to exercise just that subsystem
without the rest of the system present.