# Schematic verification — Rev B

Every net in `schematic.pdf` cross-checked against its source. This exists so a reviewer
can dispute a specific line rather than the drawing as a whole.

Sources used:

| Tag | Source |
|---|---|
| **CFG** | `firmware/config.py` on `lead/docs-and-firmware` |
| **WIRE** | `hardware/electrical/README.md`, "Wiring reference" |
| **PINOUT** | Seeed XIAO ESP32-S3 official pinout (`Micro/1.jpg`, course parts pack) |
| **L293D** | `L293D-datasheet.pdf` |
| **LED** | `Tri-color-LED-datasheet.pdf` |
| **HANDOUT** | ECE 463 Mini-Project instructions, "Hookup table" |

---

## 1. Pin-name convention — changed in Rev B

The XIAO's pads are silkscreened **D0–D10**, not GPIO numbers. A schematic that only says
"GPIO7" cannot be wired without a translation step, and the mapping is not intuitive:

| GPIO | Silkscreen | Pad no. | Source |
|---|---|---|---|
| GPIO1 | **D0** | 1 | PINOUT |
| GPIO2 | **D1** | 2 | PINOUT |
| GPIO3 | **D2** | 3 | PINOUT |
| GPIO4 | **D3** | 4 | PINOUT |
| GPIO5 | **D4** | 5 | PINOUT |
| GPIO6 | **D5** | 6 | PINOUT |
| GPIO7 | **D8** | 9 | PINOUT |
| GPIO8 | **D9** | 10 | PINOUT |
| GPIO9 | **D10** | 11 | PINOUT |
| 3V3 | 3V3 | 12 | PINOUT |
| GND | GND | 13 | PINOUT |
| 5V | 5V | 14 | PINOUT |

Note GPIO7/8/9 → D8/D9/D10: the numbers differ **and** those pads are on the opposite side
of the board from GPIO1–6. Rev A showed GPIO names only. Rev B shows `silkscreen / GPIO`
plus the pad number on every pin.

---

## 2. Net-by-net check

### Stepper drive

| Net | Schematic | CFG | WIRE | HANDOUT |
|---|---|---|---|---|
| `STEP1` | D0/GPIO1 → U2 pin 2 (1A) | `STEP_PINS = (1,…)` | GPIO1 → pin 2 | GPIO1 → Pin 2 (1A) |
| `STEP2` | D1/GPIO2 → U2 pin 7 (2A) | `STEP_PINS = (…,2,…)` | GPIO2 → pin 7 | GPIO2 → Pin 7 (2A) |
| `STEP3` | D2/GPIO3 → U2 pin 10 (3A) | `STEP_PINS = (…,3,…)` | GPIO3 → pin 10 | GPIO3 → Pin 10 (3A) |
| `STEP4` | D3/GPIO4 → U2 pin 15 (4A) | `STEP_PINS = (…,4)` | GPIO4 → pin 15 | GPIO4 → Pin 15 (4A) |

All three sources agree.

### Coils

| Net | Schematic | WIRE | HANDOUT |
|---|---|---|---|
| `COIL1` | U2 pin 3 (1Y) → orange | pin 3 → Orange | (1Y) Pin 3 → Orange |
| `COIL2` | U2 pin 6 (2Y) → pink | pin 6 → Pink | (2Y) Pin 6 → Pink |
| `COIL3` | U2 pin 11 (3Y) → yellow | pin 11 → Yellow | (3Y) Pin 11 → Yellow |
| `COIL4` | U2 pin 14 (4Y) → blue | pin 14 → Blue | (4Y) Pin 14 → Blue |
| `+5V` | red centre tap | 5V → Red | 5V → Red (+5V) |

Coil order matches the `STEP_SEQUENCE` comments in CFG: orange → pink → yellow → blue.

### L293D power

| Pin | Schematic | WIRE | Datasheet limit |
|---|---|---|---|
| 16 VCC1 | +5 V | 5V | recommended 4.5–7.0 V ✓ |
| 8 VCC2 | +5 V | 5V | VCC1 … 36 V ✓ |
| 1 EN1,2 | +3V3 | 3V3 | input, VIH(min) 2.3 V ✓ |
| 9 EN3,4 | +3V3 | 3V3 | input, VIH(min) 2.3 V ✓ |
| 4,5,12,13 | GND | GND | — |

HANDOUT says *"Pin 1 and Pin 9: Connect to VCC1 (+3.3V)"*, which is self-contradictory —
it states VCC1 = +5 V two lines earlier. WIRE resolves it as enables on 3V3, which the
datasheet supports. Drawn per WIRE. Recorded in `NOTES.md` finding 1.

### LEDs

| Net | Schematic | CFG | WIRE |
|---|---|---|---|
| `LED_R` | D8/GPIO7 → R1 220 Ω → D1 red anode | `LED_RED = 7` | GPIO7 → Red |
| `LED_B` | D9/GPIO8 → R2 220 Ω → D1 blue anode | `LED_BLUE = 8` | GPIO8 → Blue |
| `LED_G` | D10/GPIO9 → R3 220 Ω → D1 green anode | `LED_GREEN = 9` | GPIO9 → Green |
| `GND` | D1 common cathode | `COMMON_ANODE = False` | LED cathodes → GND |

LED datasheet p.1 features: *"Common Cathode"*. Consistent with `COMMON_ANODE = False` and
with `leds.py`'s comment *"increasing PWM = brighter LED"* — a higher duty on a
common-cathode part is brighter.

### Buttons

| Net | Schematic | CFG | firmware | WIRE |
|---|---|---|---|---|
| `BTN_SELECT` | D4/GPIO5 → SW1 → GND | `BTN_SELECT = 5` | `Pin(n, Pin.IN, Pin.PULL_UP)` | GPIO5, switch 1 (SELECT) |
| `BTN_START` | D5/GPIO6 → SW2 → GND | `BTN_START = 6` | same | GPIO6, switch 2 (START) |

`buttons.py` uses `Pin.PULL_UP`, so no external pull-up is drawn and pressed = logic 0.

**Rev A had these two reversed** (SW1 labelled START, SW2 labelled PRESET). Corrected.

---

## 3. Open items — not schematic errors, but flagged

**a) Coil drive polarity.** `CFG.STEP_SEQUENCE` is active-HIGH:

```python
STEP_SEQUENCE = ((1,0,0,0), (0,1,0,0), (0,0,1,0), (0,0,0,1))
```

With the centre tap at +5 V, a coil energises when its driver output goes **LOW**
(L293D VOH ≈ VCC2 − 1.4 … −1.8 V, so a HIGH output leaves only ~1.4–1.8 V across the
winding). Two consequences:

- the sequence may need inverting, and
- the all-zero idle state pulls all four outputs LOW, energising **all four coils at
  once** — the maximum-current condition.

`stepper.py` calls `release()` in `init()`, so whichever convention wins, `release()` must
write the genuinely de-energised pattern. Verify on the bench and record the result.

**b) LED brightness imbalance.** Green/blue VF = 2.8–3.6 V (LED datasheet). From 3.3 V
through 220 Ω:

```
red        ≈ (3.3 − 2.0)/220 ≈ 5.9 mA
green/blue ≈ (3.3 − 3.0)/220 ≈ 1.4 mA
green/blue at VF 3.6 V : no conduction from 3.3 V
```

`leds.py` applies the same duty scale to all three channels, so the four indication states
will not read as comparable brightness. Measure forward current per channel and scale the
duty in `leds.py`.

**c) `README.md` says the schematic was drawn in EasyEDA.** This drawing was not. Either
redraw it there or correct that line — it is a checkable claim.

---

## 4. What Rev B changed from Rev A

1. Pin names now `silkscreen / GPIO` with pad numbers — the single biggest wiring risk.
2. SW1/SW2 functions corrected against `config.py` (SELECT is GPIO5, START is GPIO6).
3. M1 drawn as four half-windings with a shared centre tap instead of a black box, so the
   unipolar topology and the reason for the LOW-side drive are visible.
4. D1 drawn inside a package outline to show it is one 4-lead part, not three LEDs.
5. Power drawn with power symbols and ground symbols rather than long rails.
6. L293D enables shown at +3V3 to match `README.md` (Rev A had them at +5 V).
