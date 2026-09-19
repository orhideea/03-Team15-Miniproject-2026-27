from machine import Pin
import time

import config

# The 28BYJ-48 needs a short settling time between coil changes. Below about
# 2 ms the rotor cannot keep up and the motor stalls or skips steps. 3 ms is a
# safe default; lower it only if the hand is visibly too slow.
STEP_INTERVAL_MS = 3

_pins = []
_position = 0  # current position, in steps above the zero mark
_target = 0  # requested position, in steps
_phase = 0  # index into config.STEP_SEQUENCE
_last_step = 0  # ticks_ms of the previous coil change
_energized = False


def init():
    """Configure the four coil pins as outputs and park at zero."""
    global _pins, _position, _target, _phase, _last_step
    _pins = [Pin(num, Pin.OUT) for num in config.STEP_PINS]
    _position = 0
    _target = 0
    _phase = 0
    _last_step = time.ticks_ms()
    release()


def move_to_fraction(fraction):
    """Request a hand position as a fraction of full scale.

    fraction is clamped to 0.0 - 1.0. This only sets the target; the motor is
    actually moved by repeated calls to update().
    """
    global _target
    if fraction < 0.0:
        fraction = 0.0
    elif fraction > 1.0:
        fraction = 1.0
    _target = int(fraction * config.SWEEP_STEPS)


def at_target():
    """True when the hand has reached the requested position."""
    return _position == _target


def update():
    """Advance the motor at most one step toward the target.

    Non-blocking: if it is not yet time for the next step, this returns without
    doing anything. That lets the LEDs keep pulsing and the buttons stay
    responsive while the hand moves.
    """
    global _position, _phase, _last_step

    if not _pins or _position == _target:
        return

    now = time.ticks_ms()
    if time.ticks_diff(now, _last_step) < STEP_INTERVAL_MS:
        return
    _last_step = now

    if _target > _position:
        _phase = (_phase + 1) % len(config.STEP_SEQUENCE)
        _position += 1
    else:
        # Walking the sequence backwards reverses the direction of rotation.
        _phase = (_phase - 1) % len(config.STEP_SEQUENCE)
        _position -= 1

    _apply(config.STEP_SEQUENCE[_phase])


def release():
    """Drop all four coils. The hand will hold position by gearbox friction."""
    global _energized
    _apply((0, 0, 0, 0))
    _energized = False


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _apply(pattern):
    """Write one step pattern out to the four coil pins."""
    global _energized
    for pin, value in zip(_pins, pattern):
        pin.value(value)
    if any(pattern):
        _energized = True


# ---------------------------------------------------------------------------
# Standalone test -- run this file on its own in Thonny to check the wiring.
# The hand should sweep smoothly to full scale, then back down to zero.
# If it jitters in place instead of turning, the coil order is wrong: try
# swapping two entries in config.STEP_SEQUENCE.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    init()
    for target in (1.0, 0.0, 0.5, 0.0):
        print("moving to", target)
        move_to_fraction(target)
        while not at_target():
            update()
        time.sleep(1)
    release()
    print("stepper test complete")
