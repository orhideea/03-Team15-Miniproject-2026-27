from machine import Pin, PWM
import time

import config

# ---------------------------------------------------------------------------
# Hardware note: set this to True if the tri-color LED is COMMON ANODE.
# On a common-anode part the shared leg goes to 3V3 and a channel lights up
# when its pin is pulled LOW, so the duty cycle has to be inverted.
# Check Tri-color-LED-datasheet.pdf and confirm on the bench before trusting it.
# ---------------------------------------------------------------------------
COMMON_ANODE = False

# State -> (color, pulsing?) mapping.
#   "select"  : idle, user is choosing a preset   -> blue, pulsing
#   "running" : timer counting down               -> green, steady
#   "paused"  : timer held                        -> green, pulsing
#   "expired" : time is up                        -> red, pulsing
_STATE_TABLE = {
    "select": ("blue", True),
    "running": ("green", False),
    "paused": ("green", True),
    "expired": ("red", True),
}

_channels = {}  # color name -> PWM object
_state = "select"  # current state name


def init():
    """Create the PWM channels. Safe to call more than once."""
    global _channels
    _channels = {
        "red": PWM(Pin(config.LED_RED), freq=config.PWM_FREQ, duty_u16=0),
        "blue": PWM(Pin(config.LED_BLUE), freq=config.PWM_FREQ, duty_u16=0),
        "green": PWM(Pin(config.LED_GREEN), freq=config.PWM_FREQ, duty_u16=0),
    }
    off()


def set_state(name):
    """Select which LED pattern to display.

    name must be one of: "select", "running", "paused", "expired".
    Unknown names are ignored so a typo in main.py cannot crash the timer.
    """
    global _state
    if name in _STATE_TABLE:
        _state = name


def update():
    """Advance the pulse animation. Call this every pass of the main loop.

    This is deliberately non-blocking -- it reads the millisecond clock and
    computes the brightness for *right now*, rather than sleeping. Using
    time.sleep() here would stall the stepper and the buttons.
    """
    if not _channels:
        return

    color, pulsing = _STATE_TABLE[_state]
    level = _pulse_level() if pulsing else 1.0

    for name, pwm in _channels.items():
        pwm.duty_u16(_duty(level) if name == color else _duty(0.0))


def off():
    """Turn all three channels fully off."""
    for pwm in _channels.values():
        pwm.duty_u16(_duty(0.0))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _pulse_level():
    """Return brightness 0.0 -> 1.0 -> 0.0 over one PULSE_PERIOD_MS window.

    A triangle wave is used rather than a sine so there is no floating point
    math library dependency; visually the difference is negligible.
    """
    period = config.PULSE_PERIOD_MS
    half = period // 2
    phase = time.ticks_ms() % period
    if phase < half:
        return phase / half  # ramping up
    return (period - phase) / half  # ramping back down


def _duty(level):
    """Convert a 0.0-1.0 brightness into a 16-bit duty value."""
    if level < 0.0:
        level = 0.0
    elif level > 1.0:
        level = 1.0
    value = int(level * 65535)
    return (65535 - value) if COMMON_ANODE else value


# ---------------------------------------------------------------------------
# Standalone test -- run this file on its own in Thonny to check the wiring.
# It walks through every state for three seconds each.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    init()
    for state in ("select", "running", "paused", "expired"):
        print("state:", state)
        set_state(state)
        end = time.ticks_add(time.ticks_ms(), 3000)
        while time.ticks_diff(end, time.ticks_ms()) > 0:
            update()
            time.sleep_ms(10)
    off()
    print("LED test complete")
