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
#   update()          -- must be called repeatedly from the main loop so the
#                        pulse animation advances. Non-blocking.
#   off()             -- turn everything off (used on shutdown / reset).

from machine import Pin, PWM
import time

import config

# ---------------------------------------------------------------------------
# Pin assignment -- VERIFIED ON THE BENCH, and NOT in numeric color order.
#
#   color   config.py    GPIO   XIAO silkscreen   pad
#   ------  -----------  -----  ----------------  ---
#   green   LED_GREEN      7    D8                 9
#   red     LED_RED        8    D9                10
#   blue    LED_BLUE       9    D10               11
#
# The obvious guess (red=7, blue=8, green=9) is what the firmware shipped with
# originally and it is wrong for this build -- driving "red" then lit the green
# die. The table above is what we measured. Pin numbers live in config.py; this
# module must never hardcode them.
#
# Note the silkscreen names: the XIAO's pads are printed D0-D10, not GPIO
# numbers, and GPIO7/8/9 are the pads marked D8/D9/D10 on the opposite edge of
# the board from GPIO1-6. Wire from the silkscreen, not from the GPIO number.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# COMMON_ANODE -- CONFIRMED, no longer an open question.
#
# The part is an INL-5TB4URGB60. Its datasheet lists "Common Cathode" in the
# features on page 1, and the bench build behaves that way: the shared leg goes
# to GND and a die lights when its pin is driven HIGH, so a larger duty cycle
# is a brighter LED and no inversion is needed.
#
# Leave this False. It exists only so that a future build using a common-anode
# part can be handled by flipping one flag instead of rewriting _duty().
# ---------------------------------------------------------------------------
COMMON_ANODE = False

# ---------------------------------------------------------------------------
# Known issue, not a wiring fault: the three dies are not equally bright.
# Datasheet forward voltages at 20 mA are red 1.6-2.4 V but green and blue
# 2.8-3.6 V. Driven from the 3.3 V rail through 220 ohm that is roughly
#
#     red         (3.3 - 2.0) / 220  ~  6 mA
#     green/blue  (3.3 - 3.0) / 220  ~  1.4 mA
#
# so red reads much brighter than green and blue, and a worst-case green or
# blue die may not conduct from 3.3 V at all. If a channel looks dead, measure
# its forward voltage before chasing a broken connection. Fixing the imbalance
# means per-channel duty scaling here (or smaller series resistors on green and
# blue); both are deliberately left out of this revision because the states are
# still legible and changing it would invalidate the tested build.
# ---------------------------------------------------------------------------

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
    """Convert a 0.0-1.0 brightness into a 16-bit duty value.

    On a common-cathode part (ours) the value passes straight through. The
    inversion branch is only reached if COMMON_ANODE is set True for a
    different LED package.
    """
    if level < 0.0:
        level = 0.0
    elif level > 1.0:
        level = 1.0
    value = int(level * 65535)
    return (65535 - value) if COMMON_ANODE else value


# ---------------------------------------------------------------------------
# Standalone test -- run this file on its own in Thonny to check the wiring.
#
# It first lights each die by name for two seconds. Watch the board: if the
# printed name does not match the color you see, the pin assignment in
# config.py does not match how the board is wired -- fix config.py, not this
# file. Then it walks every state for three seconds each.
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
