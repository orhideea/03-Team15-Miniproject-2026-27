from machine import Pin
import time

import config

# Hardware verified with Brian:
# - Both switches are wired between their GPIO pin and GND.
# - GPIO inputs use the internal pull-up resistors (Pin.PULL_UP).
# - Released = HIGH (1), pressed = LOW (0).
# - DEBOUNCE_MS = 50 was tested and verified with no double-triggering.

_buttons = []


class _Button:
    """One debounced switch with optional long-press detection."""

    def __init__(self, pin_num, short_event, long_event=None):
        self._pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        self._short_event = short_event
        self._long_event = long_event

        # Hardware confirmed: switches short the GPIO pin to GND when pressed.
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
        #
        # DEBOUNCE_MS = 50 was verified on the physical switches with no
        # double-triggering.
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
#
# Hardware verified with Brian:
# - Switches connect GPIO to GND when pressed.
# - Internal pull-ups are enabled.
# - DEBOUNCE_MS = 50 was verified with no double-triggering.
#
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
