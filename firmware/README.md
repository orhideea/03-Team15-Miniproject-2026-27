# Firmware

MicroPython source for the Team 15 meeting timer, targeting the Seeed Studio
XIAO ESP32-S3 running MicroPython v1.28.0.

## Files

| File | Purpose |
|---|---|
| `config.py` | Pin assignments, step sequence, presets, timing constants. Every other module imports from here. |
| `stepper.py` | Wave-drive control of the 28BYJ-48 through the L293D H-bridge. |
| `leds.py` | Three-color LED output with PWM pulsing. |
| `buttons.py` | Debounced switch input with short and long press detection. |
| `main.py` | Top-level state machine. Runs automatically at power-on. |

## Pin assignments

Verified on the bench by driving each pin individually and observing the
result.

| Function | GPIO |
|---|---|
| Motor coil 1 (orange) | 1 |
| Motor coil 2 (pink) | 2 |
| Motor coil 3 (yellow) | 3 |
| Motor coil 4 (blue) | 4 |
| SELECT button | 5 |
| START button | 6 |
| Green LED | 7 |
| Red LED | 8 |
| Blue LED | 9 |

The LED assignments are not in colour order. They were determined empirically
after the initial wiring did not match the expected layout, and `config.py` was
corrected to match the hardware rather than the other way round.

The tri-color LED is common cathode: its shared leg goes to ground and a
channel lights when its pin is driven high. `COMMON_ANODE` in `leds.py` is
therefore `False`.

## Design notes

All four hardware modules are **non-blocking**. Nothing calls `time.sleep()`
inside normal operation. Each module exposes an `update()` or `poll()` that is
called every pass of the main loop and returns immediately. This is what lets
the hand move, the LED pulse, and the buttons respond at the same time on a
single core with no threads.

Pin numbers appear in `config.py` and nowhere else. If the wiring changes, that
is the only file that should need editing.

## Known hardware limitation: slow stepping stalls the motor

The 28BYJ-48 will not reliably take single steps at the rate a countdown
demands. This was established on the bench with raw GPIO writes, independent of
any of the code in this folder:

| Test | Result |
|---|---|
| 400 steps at 3 ms intervals | Shaft rotates normally |
| 200 steps at 125 ms intervals | No rotation at all |

At slow rates the coil is de-energized before the rotor has been pulled fully
over, so static friction wins and the motor never breaks loose. Wave drive
makes this worse, since it energizes only one coil at a time and therefore
produces the least torque of any drive mode.

The workaround is in `main.py`: instead of asking the stepper to track the
countdown continuously, the dial position is quantized into 20 discrete
positions. The hand holds still and then moves the whole way to the next
position in one fast burst, at the 3 ms step rate the motor demonstrably
handles.

A side effect is that the hand ticks rather than sweeps, which is arguably
closer to how a mechanical clock behaves anyway, and is considerably easier to
read at a glance.

## Loading onto the board

1. Open Thonny and select **MicroPython (ESP32)** as the interpreter, with the
   XIAO's serial port.
2. Open each file and use **File > Save as... > MicroPython device** to copy it
   to the board. All five files go in the device root.
3. Reset the board. `main.py` runs automatically.

Note that editing a file in Thonny's editor is not enough. Imports resolve
against the copy on the device, so any change to `config.py`, `leds.py`,
`buttons.py` or `stepper.py` must be re-saved to the device before it takes
effect.

## Testing individual modules

`stepper.py`, `leds.py`, and `buttons.py` each have a standalone test block at
the bottom. Open one in Thonny and press Run to exercise just that subsystem
without the rest of the system present. This is how each module was brought up
and how the LED pin mapping was established.
