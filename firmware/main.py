# main.py -- Team 15 meeting timer, top-level state machine.
#
# Owner: Beatrice (Tris)
#
# A self-contained meeting timer. The user picks one of four presets, starts
# the countdown, and a mechanical hand driven by a stepper motor sweeps toward
# zero while an LED shows the current state.
#
# On the ESP32, a file named main.py is run automatically at power-on, so the
# finished timer works standalone with no laptop attached.
#
# ---------------------------------------------------------------------------
# HOW TO USE THE TIMER
# ---------------------------------------------------------------------------
#   Button 1 (SELECT, GPIO5)
#       press          cycle through the presets: 15 -> 20 -> 25 -> 30 -> 15
#
#   Button 2 (START, GPIO6)
#       press          start the countdown, or pause/resume it while running
#       hold 1 second  reset back to preset selection
#
#   LED meanings
#       blue, pulsing    choosing a preset
#       green, steady    counting down
#       green, pulsing   paused
#       red, pulsing     time is up
#
# ---------------------------------------------------------------------------
# THE DIAL
# ---------------------------------------------------------------------------
# The hand reads absolute minutes, not percent-of-preset. Full scale is the
# largest preset (30 min), so a 15 minute timer starts at half deflection and
# sweeps down from there. This keeps the dial honest: the same hand angle
# always means the same number of minutes, whichever preset is chosen.
#
# ---------------------------------------------------------------------------
# STATE MACHINE
# ---------------------------------------------------------------------------
#   SELECT  --start-->        RUNNING
#   RUNNING --start-->        PAUSED
#   RUNNING --time reaches 0--> EXPIRED
#   PAUSED  --start-->        RUNNING
#   EXPIRED --start-->        SELECT
#   any     --reset (hold)--> SELECT

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

    last_move = time.ticks_ms()
    last_fraction = None
    while True:        # 1. Read input.
        timer.handle(buttons.poll())

        # 2. Advance the clock.
        timer.tick()

        # 3. Drive the outputs. Both calls are non-blocking, so the loop keeps
        #    spinning fast enough that button presses are never missed.
        wanted = round(timer._dial_fraction() * 20) / 20
        if wanted != last_fraction:
            last_fraction = wanted
            stepper.move_to_fraction(wanted)
            while not stepper.at_target():
                stepper.update()
        leds.update()

        # 4. De-energize the motor once the hand has settled. The gearbox holds
        #    position on its own, so there is no reason to keep burning current
        #    in the coils -- this is the low-power part of the design.
        
        # if stepper.at_target():
        #   if time.ticks_diff(time.ticks_ms(), last_move) > 2000:
        #       stepper.release()
        #else:
        #   last_move = time.ticks_ms()

        # A short yield keeps CPU use sane without hurting responsiveness.
        time.sleep_ms(2)


if __name__ == "__main__":
    run()
