# config.py: shared hardware configuration for the Team 15 meeting timer.
# Every module imports from here. Do not hardcode pin numbers anywhere else.

# --- Stepper motor (28BYJ-48 via L293D H-bridge) ---
# These drive the L293D inputs 1A, 2A, 3A, 4A -> motor coils 1-4.
STEP_PINS = (1, 2, 3, 4)  # GPIO1..GPIO4

# Wave-drive sequence: one coil energized at a time.
STEP_SEQUENCE = (
    (1, 0, 0, 0),  # coil 1 - orange
    (0, 1, 0, 0),  # coil 2 - pink
    (0, 0, 1, 0),  # coil 3 - yellow
    (0, 0, 0, 1),  # coil 4 - blue
)

STEPS_PER_REV = 2048  # 28BYJ-48 full-step, after 63.68:1 gearbox
SWEEP_STEPS = 1024  # hand travels 180 deg from full to zero

# --- LEDs (each through a 220 ohm resistor) ---
LED_RED = 8
LED_BLUE = 9
LED_GREEN = 7
PWM_FREQ = 1000  # Hz, PWM carrier
PULSE_PERIOD_MS = 1000  # one full brightness breath per second

# --- Buttons (tactile switches) ---
BTN_SELECT = 5  # cycles the preset
BTN_START = 6  # short press: start/pause, long press: reset
DEBOUNCE_MS = 50
LONG_PRESS_MS = 1000

# --- Timer presets, in minutes ---
PRESETS_MIN = (1, 2, 3, 4)