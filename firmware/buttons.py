# buttons.py -- tactile switch input for the Team 15 meeting timer.
#
# Owner: Micky (Richard)
#
# Reads the two tactile switches and turns raw pin transitions into clean,
# debounced events for the state machine in main.py.
#
# Wiring assumption: each switch connects its GPIO pin to GND, and the pin uses
# the ESP32's internal pull-up. So the pin reads 1 when released and 0 when
# pressed (active low). No external resistors are needed. Confirm this with
# Brian before testing -- if the switches were wired to 3V3 instead, the logic
# below has to be inverted.
#
# Public interface (agreed with the team -- do not change without telling everyone):
#   init()   -- configure the pins. Call once at startup.
#   poll()   -- call repeatedly from the main loop. Returns None most of the
#               time, or one of: "select", "start", "reset".
#
# Event mapping:
#   BTN_SELECT, short press  -> "select"   cycle to the next preset
#   BTN_START,  short press  -> "start"    start / pause the countdown
#   BTN_START,  held 1s      -> "reset"    abandon and return to select

from machine import Pin
import time

import config

# Hardware notes (verified with Brian): both switches are wired between the
# GPIO pin and GND and use the internal pull-ups (Pin.PULL_UP). DEBOUNCE_MS = 50
# was tested on the physical switches with no double-triggering.

_buttons = []


class _Button:
    """One debounced switch with optional long-press detection."""

    def __init__(self, pin_num, short_event, long_event=None):
        self._pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        self._short_event = short_event
        self._long_event = long_event

        # 1 == released (idle, pulled high). 0 == pressed (shorted to GND).
        self._stable = 1
        self._last_raw = 1
        self._last_change = time.ticks_ms()
        self._pressed_at = 0
        self._long_fired = False

    def poll(self):
        """Return an event string, or None if nothing has happened."""
        now = time.ticks_ms()
        raw = self._pin.value()

        # The reading just changed -- restart the debounce window and wait for
        # it to settle. Mechanical switches bounce for a few milliseconds and
        # would otherwise generate a burst of phantom presses.
        if raw != self._last_raw:
            self._last_raw = raw
            self._last_change = now
            return None

        if time.ticks_diff(now, self._last_change) < config.DEBOUNCE_MS:
            return None

        # The reading has been steady long enough to trust it.
        if raw != self._stable:
            self._stable = raw
            if raw == 0:
                # Falling edge: press began. Nothing is emitted yet, because we
                # do not know if this will turn out to be short or long.
                self._pressed_at = now
                self._long_fired = False
            else:
                # Rising edge: released. Emit the short event only if the long
                # event did not already fire during the hold.
                if not self._long_fired:
                    return self._short_event
            return None

        # Still held down -- check whether it has crossed the long-press
        # threshold. Firing here (rather than on release) gives immediate
        # feedback to the user instead of waiting for them to let go.
        if self._stable == 0 and self._long_event and not self._long_fired:
            if time.ticks_diff(now, self._pressed_at) >= config.LONG_PRESS_MS:
                self._long_fired = True
                return self._long_event

        return None


def init():
    """Configure both switches. Safe to call more than once."""
    global _buttons
    _buttons = [
        _Button(config.BTN_SELECT, "select"),
        _Button(config.BTN_START, "start", long_event="reset"),
    ]


def poll():
    """Check both switches and return the first pending event, or None.

    Non-blocking by design: it never sleeps or waits for a release, so the
    stepper and LED animations keep running smoothly. Call it every pass of
    the main loop.
    """
    for button in _buttons:
        event = button.poll()
        if event is not None:
            return event
    return None


# ---------------------------------------------------------------------------
# Standalone test -- run this file on its own in Thonny to check the switches.
# Press each button and watch the shell. Hold the start button for a second to
# see the reset event.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    init()
    print("Press the buttons. Ctrl-C to stop.")
    while True:
        event = poll()
        if event:
            print("event:", event)
        time.sleep_ms(5)
