# Hardware

Electrical and mechanical documentation for the Team 15 meeting timer.

## Contents

| Folder | Contents |
|---|---|
| `electrical/` | Schematic, wiring reference, bill of materials, and component datasheets |

## On the mechanical side

There is no `mechanical/` folder in this repository. The assignment requires an
enclosure, CAD drawings, and a 3D print only if the team includes mechanical
engineers. Team 15 is composed entirely of computer engineers, so that
deliverable does not apply to this build.

The device is presented as an open breadboard assembly. The clock hand is a
popsicle stick mounted directly to the stepper motor's output shaft, as
suggested in the course hardware build notes.

## Build summary

The circuit is built on a single solderless breadboard and powered entirely
over USB-C from the Seeed Studio XIAO ESP32-S3. No external power supply is
required: the board provides 5V from USB bus power for the motor and the
driver, and 3.3V from its onboard regulator for the driver's enable pins.

The stepper motor is not driven directly from the microcontroller. An L293D
H-bridge sits between them, level shifting the 3.3V GPIO signals up to the 5V
the motor needs and keeping the motor's switching current off the
microcontroller's pins.

See `electrical/README.md` for the full pin-by-pin wiring reference.
