# Design notes — schematic review

Written while drawing `schematic.pdf`. Each item is checked against the datasheets in this
folder and against the firmware on this branch. Three of the four are things to confirm on
the bench before or during bring-up.

---

## 1. Enable pins at 3V3 — confirmed correct

The course handout is self-contradictory here. It says:

> Pin 16 (VCC1): Connect to +5V (logic power for the chip)
> Pin 1 (1,2EN) and Pin 9 (3,4EN): Connect to VCC1 (+3.3V) to enable motor channels

VCC1 cannot be both +5 V and +3.3 V. Our `hardware/electrical/README.md` resolves it as
VCC1/VCC2 = 5 V and the two enables on the XIAO 3V3 rail. **That resolution is correct**,
and the datasheet backs it:

| L293D parameter | Value | Source |
|---|---|---|
| Logic supply VCC1, recommended | 4.5 – 7.0 V | Recommended Operating Conditions |
| High-level input voltage VIH(min) | **2.3 V** | Recommended Operating Conditions |

The enables are ordinary logic inputs, so 3.3 V clears the 2.3 V threshold with margin.
VCC1 itself still has to be 5 V — 3.3 V there would be below the 4.5 V minimum. The
"(+3.3V)" in the handout is a mislabel of VCC1, not an instruction to under-volt the part.

Schematic drawn to match the README: EN1,2 and EN3,4 → +3V3, VCC1 and VCC2 → +5 V.

---

## 2. D1 is common cathode — confirms `COMMON_ANODE = False`

`firmware/leds.py` carries this note:

```python
# Hardware note: set this to True if the tri-color LED is COMMON ANODE.
# Check Tri-color-LED-datasheet.pdf and confirm on the bench before trusting it.
COMMON_ANODE = False
```

Checked. `Tri-color-LED-datasheet.pdf`, page 1, INL-5TB4URGB60 features list:

> • Common Cathode

So `COMMON_ANODE = False` is right: the shared leg goes to GND and a channel lights when
its GPIO is driven HIGH. No duty-cycle inversion needed. Still worth a meter check in
diode mode during assembly — the longest lead should be the common cathode.

---

## 3. Coil drive polarity contradicts `config.py` — needs a bench check

`firmware/config.py` encodes the wave sequence active-HIGH:

```python
STEP_SEQUENCE = (
    (1, 0, 0, 0),  # coil 1 - orange
    ...
```

With the motor's centre tap (red) tied to +5 V, current flows through a half-winding when
its end is pulled **toward ground**, not toward +5 V.

From the L293D datasheet, high-level output voltage is VOH ≈ VCC2 − 1.4 V to VCC2 − 1.8 V.
With VCC2 = 5 V a driver output driven HIGH sits near 3.2–3.6 V, leaving only ~1.4–1.8 V
across the coil. Driven LOW the coil sees roughly 4 V. So on this wiring **a LOW energises
the coil**, and the sequence as written produces weak torque or none.

Two consequences:

1. The sequence may need inverting, i.e. `(0, 1, 1, 1)` style rows, or the polarity handled
   inside `stepper.py`.
2. **More important:** with the active-HIGH table, the idle state `(0, 0, 0, 0)` pulls all
   four outputs LOW, which energises **all four coils at once**. That is the maximum
   current state and it heats both the driver and the motor continuously. GPIOs are also
   undriven during reset, so the power-on state needs to be set deliberately.

The handout anticipates the ambiguity — *"You may need to debug the ordering; feel free to
try out other patterns"* — but the all-coils-on idle state is worth fixing regardless of
which way the polarity lands.

**This does not change the schematic.** Recorded here for whoever owns `stepper.py`.
Suggested: define an explicit safe idle in `config.py` and apply it at start-up and
shutdown. Verify the real polarity on the bench and record which convention won.

---

## 4. Green and blue will be dim

`Tri-color-LED-datasheet.pdf`, Electrical Characteristics at IF = 20 mA:

| Colour | VF min | VF max |
|---|---|---|
| Red | 1.6 V | 2.4 V |
| Green | 2.8 V | **3.6 V** |
| Blue | 2.8 V | **3.6 V** |

Driven from a 3.3 V GPIO through 220 Ω:

```
Red,        VF ≈ 2.0 V : (3.3 − 2.0) / 220 ≈ 5.9 mA
Green/blue, VF ≈ 3.0 V : (3.3 − 3.0) / 220 ≈ 1.4 mA
Green/blue, VF = 3.6 V : no forward conduction from 3.3 V at all
```

Two consequences for `leds.py`:

1. **Red will be several times brighter than green and blue.** The state indications in
   the README use all three colours, so the PWM duty cycles probably need per-channel
   scaling for the three states to read as comparable brightness.
2. **A dead green or blue channel may not be a wiring fault.** At worst-case VF the die
   simply will not light from 3.3 V. Measure VF before chasing a bad connection.

220 Ω is what the BOM supplies and what the handout specifies, so this is flagged rather
than changed. Measure forward current on all three channels during bring-up and record the
numbers — that measurement either confirms this or retires it.

---

## 5. Decoupling — recommended, not in the kit

A 100 nF ceramic across VCC1–GND at the L293D and a 100 µF bulk capacitor on the +5 V rail
near pin 8. The motor is an inductive load and the same USB 5 V rail feeds the MCU, so coil
switching transients can reach the ESP32-S3 supply. Not on the BOM, so not drawn. **If the
board resets when the motor starts, this is the first thing to try.**

---

## Pre-power checklist

- [ ] U2 pin 16 → +5 V, U2 pin 8 → +5 V (continuity)
- [ ] U2 pin 1 and pin 9 → 3V3 (continuity)
- [ ] U2 pins 4, 5, 12, 13 → GND
- [ ] **No** continuity between +5 V and GND
- [ ] U2 pin-1 notch orientation matches the drawing
- [ ] M1 red on +5 V, not on a driver output
- [ ] D1 common cathode identified with a meter, wired to GND
- [ ] First power-up with the motor **disconnected**

The handout's own warning: *"Check and double check before you burn out one of the chips."*
