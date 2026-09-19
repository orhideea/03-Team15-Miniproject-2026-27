import time
import config
import leds
import buttons
import stepper

# Full scale on the dial, in minutes.
SCALE_MAX_MIN = max(config.PRESETS_MIN)

# State names. Plain strings keep the REPL output readable while debugging.
SELECT = "select"
RUNNING = "running"
PAUSED = "paused"
EXPIRED = "expired"


class Timer:
    """Holds all mutable state for the timer."""

    def __init__(self):
        self.state = SELECT
        self.preset_index = 0
        self.remaining_ms = self._preset_ms()
        self.last_tick = time.ticks_ms()

    # -- helpers ----------------------------------------------------------

    def _preset_ms(self):
        """Duration of the currently selected preset, in milliseconds."""
        return config.PRESETS_MIN[self.preset_index] * 60 * 1000

    def _dial_fraction(self):
        """Where the hand should point right now, 0.0 - 1.0."""
        minutes_left = self.remaining_ms / 60000.0
        return minutes_left / SCALE_MAX_MIN

    def _enter(self, state):
        """Move to a new state and update the LED to match."""
        self.state = state
        leds.set_state(state)
        print("state ->", state)

    # -- event handling ---------------------------------------------------

    def handle(self, event):
        """Apply a button event to the state machine."""
        if event is None:
            return

        # Reset works from anywhere, so it is handled before the per-state
        # logic rather than repeated in each branch.
        if event == "reset":
            self.remaining_ms = self._preset_ms()
            self._enter(SELECT)
            return

        if self.state == SELECT:
            if event == "select":
                # Cycle to the next preset and reload the countdown.
                self.preset_index = (self.preset_index + 1) % len(config.PRESETS_MIN)
                self.remaining_ms = self._preset_ms()
                print("preset ->", config.PRESETS_MIN[self.preset_index], "min")
            elif event == "start":
                self.last_tick = time.ticks_ms()
                self._enter(RUNNING)

        elif self.state == RUNNING:
            if event == "start":
                self._enter(PAUSED)

        elif self.state == PAUSED:
            if event == "start":
                # Restart the clock reference so the paused interval is not
                # subtracted from the remaining time.
                self.last_tick = time.ticks_ms()
                self._enter(RUNNING)

        elif self.state == EXPIRED:
            if event == "start":
                self.remaining_ms = self._preset_ms()
                self._enter(SELECT)

    # -- time keeping -----------------------------------------------------

    def tick(self):
        """Subtract elapsed real time while running."""
        now = time.ticks_ms()

        if self.state != RUNNING:
            # Keep the reference current so a resume does not lose time.
            self.last_tick = now
            return

        elapsed = time.ticks_diff(now, self.last_tick)
        self.last_tick = now
        self.remaining_ms -= elapsed

        if self.remaining_ms <= 0:
            self.remaining_ms = 0
            self._enter(EXPIRED)


def run():
    """Set up the hardware and run the main loop forever."""
    leds.init()
    buttons.init()
    stepper.init()

    timer = Timer()
    leds.set_state(timer.state)
    print(
        "Team 15 meeting timer ready. Preset:",
        config.PRESETS_MIN[timer.preset_index],
        "min",
    )

    while True:
        # 1. Read input.
        timer.handle(buttons.poll())

        # 2. Advance the clock.
        timer.tick()

        # 3. Drive the outputs. Both calls are non-blocking, so the loop keeps
        #    spinning fast enough that button presses are never missed.
        stepper.move_to_fraction(timer._dial_fraction())
        stepper.update()
        leds.update()

        # 4. De-energize the motor once the hand has settled. The gearbox holds
        #    position on its own, so there is no reason to keep burning current
        #    in the coils -- this is the low-power part of the design.
        if stepper.at_target():
            stepper.release()

        # A short yield keeps CPU use sane without hurting responsiveness.
        time.sleep_ms(2)


if __name__ == "__main__":
    run()
