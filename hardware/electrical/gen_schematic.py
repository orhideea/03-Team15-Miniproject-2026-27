#!/usr/bin/env python3
"""
Team 15 mini-project — meeting timer, electrical schematic.
Generates schematic.svg. Re-run after editing to regenerate.

Every connection in this drawing is traceable to a source:
  - firmware/config.py                     (pin assignments)
  - hardware/electrical/README.md          (wiring reference)
  - Seeed XIAO ESP32-S3 pinout (Micro/1.jpg in the course parts pack)
  - L293D datasheet
  - INL-5TB4URGB60 datasheet
See VERIFICATION.md for the line-by-line cross-check.
"""

W, H = 1700, 1240
P = []

INK, GREY = "#111111", "#6b6b6b"
RED, BLUE, GREEN = "#c0392b", "#1f4e9c", "#1e8449"
FONT = "Helvetica, Arial, sans-serif"
MONO = "'DejaVu Sans Mono', 'Courier New', monospace"


def add(s): P.append(s)

def line(x1, y1, x2, y2, c=INK, w=1.7, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" '
        f'stroke-width="{w}" stroke-linecap="round"{d}/>')

def poly(pts, c=INK, w=1.7, fill="none"):
    d = " ".join(f"{x},{y}" for x, y in pts)
    add(f'<polyline points="{d}" fill="{fill}" stroke="{c}" stroke-width="{w}" '
        f'stroke-linejoin="round" stroke-linecap="round"/>')

def rect(x, y, w, h, c=INK, sw=1.9, fill="none", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
        f'stroke="{c}" stroke-width="{sw}"{d}/>')

def txt(x, y, s, size=13, anchor="start", c=INK, family=FONT, weight="normal",
        style="normal", halo=False):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    base = (f'x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'text-anchor="{anchor}" font-weight="{weight}" font-style="{style}"')
    if halo:
        add(f'<text {base} fill="none" stroke="#ffffff" stroke-width="4.5" '
            f'stroke-linejoin="round">{s}</text>')
    add(f'<text {base} fill="{c}">{s}</text>')

def dot(x, y, c=INK, r=3.6):
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>')

def vflag(x, y, label, c=RED):
    """Power flag: stub upward from (x,y) then an arrow + label."""
    line(x, y, x, y - 18)
    poly([(x - 9, y - 18), (x, y - 29), (x + 9, y - 18), (x - 9, y - 18)], w=1.8)
    txt(x, y - 36, label, 11, "middle", c, weight="bold")

def gnd(x, y):
    """Ground symbol: stub downward from (x,y) then the bars."""
    line(x, y, x, y + 16)
    line(x - 15, y + 16, x + 15, y + 16, w=2.2)
    line(x - 10, y + 22, x + 10, y + 22, w=2.2)
    line(x - 4, y + 28, x + 4, y + 28, w=2.2)

def inductor(x1, x2, y, bumps=4):
    """Coil drawn as semicircular bumps from x1 to x2."""
    seg = (x2 - x1) / bumps
    d = f"M {x1} {y}"
    for i in range(bumps):
        a, b = x1 + i * seg, x1 + (i + 1) * seg
        d += f" A {seg/2} {seg/2} 0 0 1 {b} {y}"
    add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="1.8"/>')


# ═════════════════════════════════════════════ frame + title
add(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
rect(18, 18, W - 36, H - 36, sw=2.3)
txt(46, 54, "SELF-CONTAINED MEETING TIMER", 21, weight="bold")
txt(46, 78, "Seeed XIAO ESP32-S3  ·  L293D quad half-H driver  ·  28BYJ-48 unipolar stepper"
            "  ·  tri-colour LED  ·  2 × tactile switch", 12.5, c=GREY)

# ═════════════════════════════════════════════ U1 — XIAO ESP32-S3
ux, uy, uw, uh = 120, 230, 250, 470          # 230 .. 700
rect(ux, uy, uw, uh, sw=2.3)
txt(ux + uw / 2, uy - 36, "U1", 15, "middle", weight="bold")
txt(ux + uw / 2, uy - 17, "Seeed XIAO ESP32-S3", 12, "middle")
txt(ux + uw / 2, uy + uh + 22, "USB-C: 5 V power + MicroPython flash / REPL",
    11, "middle", c=GREY)
txt(ux + uw / 2, uy + uh + 38, "pin numbers are the board's 1–14 pad order;",
    10, "middle", c=GREY)
txt(ux + uw / 2, uy + uh + 52, "names shown as  silkscreen / GPIO", 10, "middle", c=GREY)

# left-hand power pins:  (pad no, label, y)
for pad, lbl, y in [("14", "5V", 270), ("13", "GND", 350), ("12", "3V3", 450)]:
    line(ux - 42, y, ux, y)
    txt(ux + 14, y + 4, lbl, 12, family=MONO)
    txt(ux - 8, y - 9, pad, 10, "end", c=GREY, family=MONO)

vflag(ux - 42, 270, "+5V")
gnd(ux - 42, 350)
vflag(ux - 42, 450, "+3V3")

# right-hand signal pins: (pad no, silkscreen, gpio, y)
SIG = [("1", "D0", "GPIO1", 280), ("2", "D1", "GPIO2", 320),
       ("3", "D2", "GPIO3", 360), ("4", "D3", "GPIO4", 400),
       ("9", "D8", "GPIO7", 460), ("10", "D9", "GPIO8", 510),
       ("11", "D10", "GPIO9", 560),
       ("5", "D4", "GPIO5", 620), ("6", "D5", "GPIO6", 660)]
for pad, silk, gpio, y in SIG:
    line(ux + uw, y, ux + uw + 40, y)
    txt(ux + uw - 14, y + 4, f"{silk} / {gpio}", 12, "end", family=MONO)
    txt(ux + uw + 8, y - 9, pad, 10, "start", c=GREY, family=MONO)

# ═════════════════════════════════════════════ U2 — L293D
lx, ly, lw, lh = 720, 240, 270, 280          # 240 .. 520
rect(lx, ly, lw, lh, sw=2.3)
add(f'<path d="M {lx+lw/2-15} {ly} a 15 15 0 0 0 30 0" fill="none" '
    f'stroke="{INK}" stroke-width="1.9"/>')
txt(lx + lw / 2, ly - 74, "U2", 15, "middle", weight="bold")
txt(lx + lw / 2, ly - 55, "L293D  quad half-H driver", 12, "middle")

for pad, nm, y in [("2", "1A", 280), ("7", "2A", 320), ("10", "3A", 360), ("15", "4A", 400)]:
    line(ux + uw + 40, y, lx, y)
    txt(lx + 14, y + 4, nm, 12, family=MONO)
    txt(lx - 8, y - 9, pad, 10, "end", c=GREY, family=MONO)

for pad, nm, y in [("3", "1Y", 280), ("6", "2Y", 320), ("11", "3Y", 360), ("14", "4Y", 400)]:
    line(lx + lw, y, lx + lw + 40, y)
    txt(lx + lw - 14, y + 4, nm, 12, "end", family=MONO)
    txt(lx + lw + 8, y - 9, pad, 10, "start", c=GREY, family=MONO)

for pad, nm, x, lbl in [("1", "EN1,2", 762, "+3V3"), ("16", "VCC1", 822, "+5V"),
                        ("8", "VCC2", 882, "+5V"), ("9", "EN3,4", 942, "+3V3")]:
    vflag(x, ly, lbl)
    txt(x, ly + 28, nm, 10.5, "middle", family=MONO)
    txt(x - 7, ly - 8, pad, 10, "end", c=GREY, family=MONO)

# ground pins tied together then one symbol
for pad, x in [("4", 762), ("5", 822), ("12", 882), ("13", 942)]:
    line(x, ly + lh, x, 572)
    txt(x, ly + lh - 14, pad, 10, "middle", c=GREY, family=MONO)
    dot(x, 572)
line(762, 572, 942, 572, w=2.0)
gnd(852, 572)
txt(lx + lw / 2, 616, "pins 4, 5, 12, 13 — GND and heat slug", 10.5, "middle", c=GREY)

# ═════════════════════════════════════════════ M1 — 28BYJ-48 unipolar stepper
COM_X = 1420
rect(1090, 232, 420, 210, sw=1.4, dash="7 6", c=GREY)
txt(1300, 214, "M1", 15, "middle", weight="bold")
txt(1300, 464, "28BYJ-48  ·  5-wire, 4-phase unipolar  ·  wave drive, one coil at a time",
    11, "middle", c=GREY)

COILS = [("ORANGE", "coil 1", 280, "#e07b20"), ("PINK", "coil 2", 320, "#d45f8e"),
         ("YELLOW", "coil 3", 360, "#c9a227"), ("BLUE", "coil 4", 400, "#2a5db0")]
for nm, cl, y, col in COILS:
    line(lx + lw + 40, y, 1170, y, c=col, w=2.1)          # driver output -> coil
    inductor(1170, 1330, y)
    line(1330, y, COM_X, y)
    dot(COM_X, y)
    txt(1140, y - 10, nm, 9.5, "middle", c=col, family=MONO)
    txt(1250, y - 22, cl, 9.5, "middle", c=GREY)

line(COM_X, 280, COM_X, 400, w=2.0)                        # centre-tap bus
line(COM_X, 212, COM_X, 280, w=2.0)
vflag(COM_X, 212, "+5V")
txt(COM_X + 16, 336, "RED", 10.5, family=MONO, c=RED)
txt(COM_X + 16, 350, "common tap", 9.5, c=GREY)

# ═════════════════════════════════════════════ D1 — tri-colour LED
txt(398, 417, "D1   tri-colour LED, COMMON CATHODE", 11.5, "start", weight="bold")
txt(398, 431, "one 4-lead package · INL-5TB4URGB60", 9.5, "start", c=GREY)
CATH_X = 648
rect(556, 440, 112, 148, sw=1.4, dash="7 6", c=GREY)      # package outline

for rn, y, col, cname in [("R1", 460, GREEN, "GREEN"), ("R2", 510, RED, "RED"),
                          ("R3", 560, BLUE, "BLUE")]:
    rx, rw, rh = 470, 56, 18
    line(ux + uw + 40, y, rx - rw / 2, y)
    rect(rx - rw / 2, y - rh / 2, rw, rh, sw=1.7)
    txt(rx, y - rh / 2 - 7, rn, 11, "middle")
    txt(rx, y + rh / 2 + 13, "220 Ω", 10, "middle", c=GREY, halo=True)
    line(rx + rw / 2, y, 576, y)

    poly([(576, y - 11), (576, y + 11), (596, y), (576, y - 11)], w=1.7)   # LED
    line(596, y - 12, 596, y + 12, w=2.3)
    line(596, y, CATH_X, y)
    for k in (0, 1):
        sx, sy = 580 + k * 8, y - 15 - k * 4
        line(sx, sy, sx + 10, sy - 10, c=col, w=1.4)
        poly([(sx + 10, sy - 10), (sx + 5.5, sy - 8), (sx + 8, sy - 5.5)],
             c=col, w=1.1, fill=col)
    txt(682, y + 4, cname, 10, "start", c=col, weight="bold")
    if y != 560:
        dot(CATH_X, y)

line(CATH_X, 460, CATH_X, 604, w=2.0)
gnd(CATH_X, 604)

# ═════════════════════════════════════════════ SW1 / SW2
def pushbutton(x, y, name, silk_gpio):
    """Normally-open momentary switch, vertical, terminals at y∓42."""
    line(x, y - 42, x, y - 15); dot(x, y - 15)
    line(x, y + 15, x, y + 42); dot(x, y + 15)
    line(x, y + 15, x + 21, y - 11, w=1.9)        # blade
    line(x + 11, y - 2, x + 11, y - 27, w=1.5)    # actuator stem
    line(x + 2, y - 27, x + 20, y - 27, w=2.1)    # cap
    txt(x - 16, y - 24, name, 11.5, "end", weight="bold", halo=True)
    txt(x - 16, y - 10, silk_gpio, 10, "end", c=GREY, family=MONO, halo=True)

line(ux + uw + 40, 620, 440, 620); line(440, 620, 440, 738)
line(ux + uw + 40, 660, 580, 660); line(580, 660, 580, 738)
pushbutton(440, 780, "SW1  SELECT", "D4 / GPIO5")
pushbutton(580, 780, "SW2  START", "D5 / GPIO6")
gnd(440, 822)
gnd(580, 822)
txt(510, 886, "switch to GND, ESP32-S3 internal pull-up enabled in firmware",
    10.5, "middle", c=GREY)
txt(510, 900, "pressed = logic 0", 10.5, "middle", c=GREY)

# ═════════════════════════════════════════════ notes
txt(52, 946, "NOTES", 13, weight="bold")
NOTES = [
 "1.  Pin names are given as silkscreen / GPIO. The XIAO's pads are printed D0–D10, not GPIO numbers — GPIO7/8/9 are the pads marked D8/D9/D10. "
 "Wire from the silkscreen name. Source: Seeed XIAO ESP32-S3 pinout.",
 "2.  L293D VCC1 (pin 16) and VCC2 (pin 8) at +5 V; EN1,2 (pin 1) and EN3,4 (pin 9) at +3V3. Datasheet: VCC1 recommended 4.5–7.0 V, VIH(min) = 2.3 V, "
 "so 3.3 V is a valid logic high on the enables but would be out of spec on VCC1.",
 "3.  GPIO logic is 3.3 V. No level shifter on the L293D inputs; the shift to the 5 V motor rail happens at the driver outputs.",
 "4.  M1 is unipolar: the four half-windings share the red centre tap, which sits at +5 V. A coil therefore energises when its driver output is pulled LOW. "
 "firmware/config.py STEP_SEQUENCE is written active-HIGH — verify on the bench (see VERIFICATION.md).",
 "5.  D1 is a single 4-lead common-cathode package, confirming COMMON_ANODE = False in firmware/leds.py. Green and blue VF = 2.8–3.6 V, so from 3.3 V "
 "through 220 Ω they draw only ~1–2 mA against red's ~6 mA; expect a large brightness imbalance.",
 "6.  LED channel order is NOT red/blue/green by GPIO number: GPIO7 drives GREEN, GPIO8 drives RED, GPIO9 drives BLUE. This is the bench-verified "
 "assignment in firmware/config.py on lead/final (LED_GREEN = 7, LED_RED = 8, LED_BLUE = 9). Rev B and the wiring table in "
 "hardware/electrical/README.md still show the original guess and are stale.",
 "7.  Not supplied in the kit, recommended: 100 nF ceramic across VCC1–GND at U2, and 100 µF bulk on the +5 V rail near pin 8.",
]
yy = 970
for n in NOTES:
    words, lineb = n.split(" "), ""
    for wd in words:
        if len(lineb) + len(wd) > 168:
            txt(52, yy, lineb, 10.5); yy += 15; lineb = "     " + wd
        else:
            lineb = (lineb + " " + wd) if lineb else wd
    txt(52, yy, lineb, 10.5); yy += 18

# ═════════════════════════════════════════════ title block
tx, ty, tw, th = 1190, 1062, 470, 132
rect(tx, ty, tw, th, sw=2.1)
for dy in (36, 68, 100):
    line(tx, ty + dy, tx + tw, ty + dy, w=1.4)
line(tx + 268, ty + 36, tx + 268, ty + th, w=1.4)
txt(tx + 14, ty + 25, "MEETING TIMER — ELECTRICAL SCHEMATIC", 14, weight="bold")
txt(tx + 14, ty + 57, "EC 463 Mini-Project · Team 15 (Group B)", 11.5)
txt(tx + 14, ty + 89, "Drawn by: Deniz Oge", 11.5)
txt(tx + 14, ty + 121, "Checked against firmware/config.py", 11.5)
txt(tx + 280, ty + 57, "Sheet 1 of 1", 11.5)
txt(tx + 280, ty + 89, "Rev C", 11.5)
txt(tx + 280, ty + 121, "2026-09-19", 11.5)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'viewBox="0 0 {W} {H}">' + "".join(P) + "</svg>")
open("/home/claude/mp/hardware/electrical/schematic.svg", "w").write(svg)
print("written", len(svg))
