# Electrical

Schematic, wiring reference, and bill of materials for the Team 15 meeting
timer.

| File | Contents |
|---|---|
| `schematic.pdf` | Schematic of the device |
| `Minproject-BOM-2026.xlsx` | Bill of materials, with Digikey source links and datasheets |
| `L293D-datasheet.pdf` | H-bridge driver datasheet |
| `Tri-color-LED-datasheet.pdf` | LED datasheet |

The schematic was drawn in EasyEDA. Fritzing was not used, per the assignment
instructions.

---

## Wiring reference

This is the netlist the schematic is drawn from, and the same table the
firmware's `config.py` encodes.

### Stepper motor path

| XIAO ESP32-S3 | L293D input | L293D output | 28BYJ-48 |
|---|---|---|---|
| GPIO1 | pin 2 (1A) | pin 3 (1Y) | Orange -- coil 1 |
| GPIO2 | pin 7 (2A) | pin 6 (2Y) | Pink -- coil 2 |
| GPIO3 | pin 10 (3A) | pin 11 (3Y) | Yellow -- coil 3 |
| GPIO4 | pin 15 (4A) | pin 14 (4Y) | Blue -- coil 4 |
| 5V | -- | -- | Red -- common (+5V) |

### L293D power and enables

| L293D pin | Connects to | Purpose |
|---|---|---|
| 16 (VCC1) | 5V | Logic supply |
| 8 (VCC2) | 5V | Motor supply |
| 1 (1,2EN) | 3V3 | Enables channels 1 and 2 |
| 9 (3,4EN) | 3V3 | Enables channels 3 and 4 |
| 4, 5, 12, 13 | GND | Ground |

The enable pins only need a logic high, and 3.3V is comfortably above the
L293D's input threshold, so they are tied to the XIAO's 3V3 rail rather than
5V.

Both VCC1 and VCC2 must be at 5V. During bring-up the breadboard's positive
rail was initially fed from the 3V3 pin rather than the 5V pin, which left the
chip's logic supply missing and the motor completely silent on all four coils.
Worth checking first if the motor does not respond.

### LEDs and switches

| XIAO pin | Component | Notes |
|---|---|---|
| GPIO7 | Green LED | Through a 220 ohm series resistor |
| GPIO8 | Red LED | Through a 220 ohm series resistor |
| GPIO9 | Blue LED | Through a 220 ohm series resistor |
| GPIO5 | Tactile switch 1 (SELECT) | To GND, internal pull-up enabled in firmware |
| GPIO6 | Tactile switch 2 (START) | To GND, internal pull-up enabled in firmware |

The LED pin order is not the obvious one. It was established empirically by
driving each pin individually and observing which colour lit, after the initial
assumed mapping did not match the board. The firmware was corrected to match
the hardware.

The tri-color LED is common cathode: the shared leg goes to the ground rail and
a channel lights when its pin is driven high. Connecting the shared leg to the
positive rail instead leaves only about 1.7V across each channel, which makes
red glow faintly and prevents blue and green from lighting at all.

The switches use the ESP32's internal pull-up resistors, so a pressed button
reads logic 0 and no external resistors are required.

---

## Power

The whole device is powered from the USB-C connection to the XIAO. The board
supplies 5V from USB bus power and 3.3V from its onboard regulator, which is
why no external supply is needed.

The L293D is required because the motor runs at 5V while the XIAO's GPIO only
swings to 3.3V. Beyond level shifting, it keeps motor switching current off the
microcontroller's pins. The "D" suffix indicates internal flyback diodes, which
clamp the inductive kickback from the motor coils.
