# Team 15 Miniproject -- Meeting Timer

A self-contained meeting timer built on a Seeed Studio XIAO ESP32-S3 running
MicroPython. The user selects one of four preset durations, starts the
countdown, and a mechanical clock hand driven by a stepper motor sweeps toward
zero while a tri-color LED indicates the current state.

---

## Team

| Role | Named Members |
|------|---------|
| Mechanical Engineering | *(none on this team -- enclosure deliverable does not apply)* |
| Electrical Engineering | *(none on this team -- electrical work covered by the CEs below)* |
| Computer Engineering | Bharath Srividhya (Team Lead), Beatrice "Tris" Vrinceanu-Popescu, Brian Quijada Pleitez, Deniz Oge, Richard "Micky" Kalich |
| Biomedical Engineering | |

---

## Repository Structure

```
.
├── firmware/          # MicroPython source code for the XIAO ESP32-S3
├── hardware/
│   └── electrical/    # Schematic, wiring table, and BOM
└── docs/              # State chart, project overview, photos
```

`hardware/mechanical/` is intentionally absent: the team has no MEs, so the
enclosure and CAD deliverables do not apply to this build.

---

## Hardware

| Component | Notes |
|-----------|-------|
| Seeed Studio XIAO ESP32-S3 | Main microcontroller. MicroPython v1.28.0. Powered and programmed over USB-C. Supplies both 5V (from USB) and 3.3V (from its regulator). |
| 28BYJ-48 stepper motor | 5-wire, 4-phase unipolar. Drives the clock hand. Run in wave drive, one coil energized at a time. |
| L293D H-bridge driver | Level-shifts the 3.3V GPIO signals to the 5V the motor needs, and isolates motor current from the micro. The "D" suffix means it has internal flyback diodes. |
| Tri-color LED | Red, blue, and green channels on three GPIO pins, each through a 220 ohm current-limiting resistor. Driven by PWM for the pulsing effect. |
| 220 ohm resistors (x3) | Current limiting, one per LED channel. |
| Tactile switches (x2) | User input. Wired to GND and read with the ESP32's internal pull-ups, so no external resistors are required. |
| Clock hand | Popsicle stick mounted to the stepper shaft. |
| Breadboard and jumper wires | Assembly. |

### Pin assignments

| XIAO pin | Connects to | Purpose |
|---|---|---|
| GPIO1 | L293D pin 2 (1A) | Motor coil 1 (orange) |
| GPIO2 | L293D pin 7 (2A) | Motor coil 2 (pink) |
| GPIO3 | L293D pin 10 (3A) | Motor coil 3 (yellow) |
| GPIO4 | L293D pin 15 (4A) | Motor coil 4 (blue) |
| GPIO5 | Tactile switch 1 | SELECT button |
| GPIO6 | Tactile switch 2 | START / PAUSE / RESET button |
| GPIO7 | Green LED (via 220R) | Status output |
| GPIO8 | Red LED (via 220R) | Status output |
| GPIO9 | Blue LED (via 220R) | Status output |
| 5V | L293D pins 8 and 16, motor red wire | Motor and logic supply |
| 3V3 | L293D pins 1 and 9 | Channel enables |
| GND | L293D pins 4, 5, 12, 13; LED cathodes; switches | Common ground |

---

## How to Use the Timer

**Button 1 (SELECT)**
- Press to cycle through the presets: 15 -> 20 -> 25 -> 30 minutes, then back to 15.

**Button 2 (START)**
- Press to start the countdown, or to pause and resume while running.
- Hold for one second to reset back to preset selection from any state.

**LED indications**

| Appearance | Meaning |
|---|---|
| Blue, pulsing | Selecting a preset |
| Green, steady | Counting down |
| Green, pulsing | Paused |
| Red, pulsing | Time is up |

**The dial.** The hand reads absolute minutes rather than percent of the
selected preset. Full scale is the largest preset (30 minutes), so a 15 minute
timer begins at half deflection. This keeps the reading consistent: the same
hand angle always means the same number of minutes remaining.

There is no limit switch, so the firmware cannot sense the hand's physical
position. By convention the hand is assumed to be at the zero mark at power-on.

---

## Demonstration

Photo of the assembled device: `docs/device-photo.jpg`

Video of the timer in operation (under 10 seconds), stored in the team Google
Drive folder under `/video`: [Watch the demo](https://drive.google.com/file/d/1BNmxIVX1rbS_jLAZKSKbm_UenGejjy32/view?usp=sharing)

---

## Team Responsibilities

Any discipline can do any role here -- you make the assignments. This team is
entirely CEs, so the electrical work was distributed among the group.

### Electrical oriented
- Produce the breadboard schematic -- **Brian**
- Summarize the bill of materials -- **Brian**
- Wire the circuit on the breadboard, verify the components are assembled
  correctly, validate the voltage levels -- **Brian**

### Computer oriented
- Design the software based on the required functionality -- **Bharath**
- Shared hardware configuration and module interfaces (`config.py`) -- **Bharath**
- Stepper motor driver (`stepper.py`) -- **Tris**
- LED output and PWM pulsing (`leds.py`) -- **Deniz**
- Button input and debouncing (`buttons.py`) -- **Micky**
- Top-level state machine (`main.py`) -- **Tris**
- Flash and test the firmware on the target micro -- **all members, individually**
- Document the APIs for the system -- **Bharath**

### Project management
- Team board, task assignment, and documentation -- **Bharath (Team Lead)**

---

## Deliverables

- [ ] Functional MicroPython firmware
- [ ] Completed breadboard assembly per schematic
- [x] ~~Fabricated and assembled enclosure~~ -- not applicable, no MEs on this team
- [ ] Documentation in this repository
- [ ] Video recording demonstrating required function (stored in google drive)

---

## Software Architecture

All hardware modules are **non-blocking**. Nothing calls `time.sleep()` during
normal operation. Each module exposes a `poll()` or `update()` that is called
once per pass of the main loop and returns immediately. This is what allows the
hand to move, the LED to pulse, and the buttons to stay responsive at the same
time, on a single core, without threads.

Pin numbers live in `config.py` and nowhere else, so a wiring change touches
exactly one file.

### Module interfaces

```
config.py    constants only -- pins, step sequence, presets, timing
stepper.py   init(), move_to_fraction(f), update(), at_target(), release()
leds.py      init(), set_state(name), update(), off()
buttons.py   init(), poll() -> None | "select" | "start" | "reset"
main.py      imports the above and runs the state machine
```

### State machine

```
SELECT  --start-------------> RUNNING
RUNNING --start-------------> PAUSED
RUNNING --time reaches 0----> EXPIRED
PAUSED  --start-------------> RUNNING
EXPIRED --start-------------> SELECT
any     --hold start 1s-----> SELECT
```

The full state chart is in `docs/`.

---

## Contribution Workflow

We want each team member to contribute work products and to host these
including documentation in the repo with version control (software,
firmware, schematics, BOMs, CAD models, etc.) All can be managed in
the repo with version control.

1. Establish that each teammember has properly set up Git/GitHub Desktop
2. Decompose the project into units to assign to each named team member
3. From the team repo, create a branch from `main` named `<role>/<feature>` (e.g., `ce/leds`) to capture work artifacts
4. Fetch the branch to the local laptop
5. Each team member does their work and produces work artifacts and commits these changes to the branch
6. Commit changes with descriptive messages
7. Open a pull request and request review from at least one other team member
8. Merge to main after approval

When performed properly, this workflow leads to an organized set of
work products that are developed concurrently and collaboratively with
version control. This includes the products themselves (e.g.,
firmware, CAD, schematics, etc.) and the associated documentation

---

## References

- Seeed Studio XIAO ESP32-S3 getting started guide:
  https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/
- XIAO ESP32-S3 with MicroPython:
  https://wiki.seeedstudio.com/xiao_esp32s3_with_micropython/
- MicroPython firmware downloads for ESP32_GENERIC_S3:
  https://micropython.org/download/ESP32_GENERIC_S3/
- L293D and 28BYJ-48 datasheets, and the project BOM, are in
  `hardware/electrical/`
- Course-provided hardware build notes and hookup table (ECE 463 Miniproject
  instructions)

---