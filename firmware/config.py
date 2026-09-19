"""Shared hardware configuration for the Team 15 meeting timer.

Every module imports its constants from this file. Do not hardcode pin
numbers or timing values anywhere else in the project.
"""

# ---------------------------------------------------------------------------
# Stepper motor: 28BYJ-48 driven through an L293D H-bridge
# ---------------------------------------------------------------------------

# GPIO pins wired to L293D inputs 1A, 2A, 3A and 4A (motor coils 1-4).
STEP_PINS = (1, 2, 3, 4)

# Wave-drive sequence: one coil energized at a time.
STEP_SEQUENCE = (
    (1, 0, 0, 0),  # Coil 1 (orange)
    (0, 1, 0, 0),  # Coil 2 (pink)
    (0, 0, 1, 0),  # Coil 3 (yellow)
    (0, 0, 0, 1),  # Coil 4 (blue)
)

STEPS_PER_REV = 2048  # Full steps per revolution, after the 63.68:1 gearbox
SWEEP_STEPS = 1024    # Steps for the hand to travel 180 degrees, full to zero

# ---------------------------------------------------------------------------
# LEDs: each connected through a 220 ohm resistor
# ---------------------------------------------------------------------------

LED_RED = 8
LED_BLUE = 9
LED_GREEN = 7

PWM_FREQ = 1000         # PWM carrier frequency, in Hz
PULSE_PERIOD_MS = 1000  # One full brightness "breath" per second

# ---------------------------------------------------------------------------
# Buttons: tactile switches
# ---------------------------------------------------------------------------

BTN_SELECT = 5  # Cycles through the timer presets
BTN_START = 6   # Short press: start/pause. Long press: reset

DEBOUNCE_MS = 50
LONG_PRESS_MS = 1000  # Press duration that counts as a "long press"

# ---------------------------------------------------------------------------
# Timer presets, in minutes
# ---------------------------------------------------------------------------

PRESETS_MIN = (15, 20, 25, 30)