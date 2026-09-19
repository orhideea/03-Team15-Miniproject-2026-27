# leds.py -- tri-color LED output for the Team 15 meeting timer.
#
# Owner: Deniz
#
# Drives the three dies of a single tri-color LED package on separate GPIO
# pins, each through a 220 ohm current-limiting resistor, using hardware PWM.
# The duty cycle is swept up and down once per second to produce a "breathing"
# pulse, as required by the assignment.
#
# Public interface (agreed with the team -- do not change without telling everyone):
#   init()            -- set up the PWM channels. Call once at startup.
#   set_state(name)   -- choose which color/pattern is showing.
#   update()          -- call repeatedly from the main loop so the pulse
#                        animation advances. Non-blocking.
#   off()             -- turn everything off.

from machine import Pin, PWM
import time

import config

# Pin assignment, verified on the bench by driving each pin individually:
# green on GPIO7, red on GPIO8, blue on GPIO9. This is not numeric color
# order -- the original guess of red=7, blue=8, green=9 lit the wrong dies,
# and config.py was corrected to match the hardware. Pin numbers live in
# config.py and must never be hardcoded here.
#
# When wiring, note the XIAO's pads are silkscreened D0-D10 rather than with
# GPIO numbers: GPIO7, 8 and 9 are the pads marked D8, D9 and D10.

# The LED is common cathode: the shared leg goes to GND and a die lights when
# its pin is driven high, so a larger duty cycle is brighter and no inversion
# is needed. This flag exists only so a future common-anode part can be
# handled by flipping one value instead of rewriting _duty().
COMMON_ANODE = False

# State -> (color, pulsing?) mapping.
_STATE_TABLE = {
    "select": ("blue", True),  # idle, choosing a preset
    "running": ("green", False),  # counting down
    "paused": ("green", True),  # held
    "expired": ("red", True),  # time is up
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
    """Advance the pulse animation. Call every pass of the main loop.

    Deliberately non-blocking: it reads the millisecond clock and computes the
    brightness for right now rather than sleeping. A time.sleep() here would
    stall the stepper and drop button presses.
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


def _pulse_level():
    """Return brightness 0.0 -> 1.0 -> 0.0 over one PULSE_PERIOD_MS window.

    A triangle wave rather than a sine, so there is no dependency on the
    floating point math library. Visually the difference is negligible.
    """
    period = config.PULSE_PERIOD_MS
    half = period // 2
    phase = time.ticks_ms() % period
    if phase < half:
        return phase / half
    return (period - phase) / half


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
#
# It lights each die by name for two seconds. If the printed name does not
# match the color on the board, the pin assignment in config.py does not match
# the wiring: fix config.py, not this file. Then it walks every state.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    init()

    _pins = {"red": config.LED_RED, "green": config.LED_GREEN, "blue": config.LED_BLUE}
    for name in ("red", "green", "blue"):
        print("die:", name, "-> GPIO", _pins[name])
        for other, pwm in _channels.items():
            pwm.duty_u16(_duty(1.0 if other == name else 0.0))
        time.sleep(2)
    off()

    for state in ("select", "running", "paused", "expired"):
        print("state:", state)
        set_state(state)
        end = time.ticks_add(time.ticks_ms(), 3000)
        while time.ticks_diff(end, time.ticks_ms()) > 0:
            update()
            time.sleep_ms(10)
    off()
    print("LED test complete")
