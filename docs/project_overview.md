# Project Overview

## Goal

Build a self-contained meeting timer using the parts provided in the course
kit, and in doing so establish the team's development workflow: a shared GitHub
repository, a task board, per-member environments capable of flashing the
microcontroller, and documentation covering the electrical and software sides
of a hardware project.

The device itself is a countdown timer for meetings. The user selects one of
four preset durations, starts the countdown, and a mechanical clock hand driven
by a stepper motor shows the time remaining while a tri-color LED indicates the
current state.

The technical exercise deliberately revisits skills from earlier coursework:
Python programming (EK 125), microcontrollers and actuators (EK 130, EK 210),
and basic circuits (EK 307).

## Deliverables

### Required functionality

- [x] Presets for 15, 20, 25, and 30 minutes
- [x] Mechanical clock hand showing time remaining, driven by the stepper motor
- [x] Buttons controlling the operation of the unit
- [x] LEDs as output -- three colors, pulsing via PWM
- [x] Enclosure with CAD drawings -- **not applicable**, no MEs on this team

### Required documentation

- [x] Project summary in Markdown (root `README.md`)
- [ ] Description of the device
- [ ] Photo(s) of the device
- [x] Description of how to use the device
- [ ] Link to a video of the device in operation (under 10 seconds), stored in
      the team Google Drive folder under `/video`
- [x] References to source materials used
- [x] State chart and flowchart of the system (`docs/state-chart.md`)
- [ ] Schematic of the device (no Fritzing)
- [x] Code folder with embedded comments (`firmware/`)
- [ ] Simple `readme.md` in each subfolder

### Technical building blocks demonstrated

| Building block | Where |
|---|---|
| GPIO | `firmware/stepper.py`, `firmware/buttons.py` |
| PWM | `firmware/leds.py` |
| LEDs | `firmware/leds.py` |
| Motor control | `firmware/stepper.py` |
| Low-power operation | `firmware/stepper.py` -- coils de-energized once the hand settles |

## Team and Roles

| Member | Role | Contribution |
|---|---|---|
| Bharath Srividhya | Team Lead | Task board, software architecture, `config.py`, documentation |
| Beatrice "Tris" Vrinceanu-Popescu | Developer | Repository setup, `stepper.py`, `main.py` |
| Brian Quijada Pleitez | Hardware | Breadboard assembly, schematic, bill of materials |
| Deniz Oge | Developer | `leds.py` -- PWM output |
| Richard "Micky" Kalich | Developer | `buttons.py` -- debounced input |

## Approach

The project was decomposed by **module**, not by feature, so that team members
could work in parallel without editing the same lines of code. A shared
`config.py` fixes the pin assignments and the function signatures each module
exposes; everything else imports from it. That interface contract was agreed
before any module was written, which is what made concurrent development
possible.

Each module can also be run standalone in Thonny to exercise just that
subsystem, so hardware faults could be isolated without the rest of the system
present.

## Known Limitations

- **No limit switch.** The firmware cannot sense the hand's physical position,
  so it is assumed to start at the zero mark at power-on.
- **Timing accuracy.** The countdown uses the microcontroller's millisecond
  tick rather than a real-time clock, which is adequate for meeting-length
  intervals but will drift over hours.
- **Power.** The device runs from USB. There is no battery option in this
  build.
