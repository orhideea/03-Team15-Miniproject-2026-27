# main.py -- Team 15 meeting timer, top-level state machine.
#
# Owner: Bharath Srividhya
#
# The user picks one of four presets, starts the countdown, and a mechanical
# hand driven by a stepper motor shows the time remaining while a tri-color
# LED indicates the current state.
#
# On the ESP32 a file named main.py runs automatically at power-on, so the
# finished timer works standalone with no laptop attached.
#
# Controls
#   Button 1 (SELECT)  press          cycle presets: 15 -> 20 -> 25 -> 30 min
#   Button 2 (START)   press          start, or pause/resume while running
#                      hold 1 second  reset back to preset selection
#
# LED
#   blue pulsing    choosing a preset
#   green steady    counting down
#   green pulsing   paused
#   red pulsing     time is up
#
# The dial reads absolute minutes rather than percent of the chosen preset.
# Full scale is the largest preset, so a 15 minute timer starts at half
# deflection. The same hand angle therefore always means the same number of
# minutes remaining, whichever preset is active.

import time

import config
import leds
import buttons
import stepper

# Full scale on the dial, in minutes.
SCALE_MAX_MIN = max(config.PRESETS_MIN)

# Number of discrete positions the dial is quantized into. See the note in the
# main loop for why the hand moves in steps rather than continuously.
DIAL_DIVISIONS = 20

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

    def _preset_ms(self):
        """Duration of the currently selected preset, in milliseconds."""
        return config.PRESETS_MIN[self.preset_index] * 60 * 1000

    def dial_fraction(self):
        """Where the hand should point right now, 0.0 to 1.0."""
        minutes_left = self.remaining_ms / 60000.0
        return minutes_left / SCALE_MAX_MIN

    def _enter(self, state):
        """Move to a new state and update the LED to match."""
        self.state = state
        leds.set_state(state)
        print("state ->", state)

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

    last_fraction = None

    while True:
        timer.handle(buttons.poll())
        timer.tick()

        # The 28BYJ-48 will not step reliably at the slow rate a countdown
        # demands: static friction stalls the rotor between single pulses.
        # Measured on the bench -- 400 steps at 3 ms apart turns the shaft,
        # while 200 steps at 125 ms apart produces no rotation at all.
        #
        # So the dial is quantized into DIAL_DIVISIONS positions and each
        # change is driven to completion in one fast burst, at the step rate
        # the motor demonstrably handles. The hand ticks rather than sweeps,
        # which is also easier to read at a glance.
        wanted = round(timer.dial_fraction() * DIAL_DIVISIONS) / DIAL_DIVISIONS
        if wanted != last_fraction:
            last_fraction = wanted
            stepper.move_to_fraction(wanted)
            while not stepper.at_target():
                stepper.update()

        leds.update()

        # A short yield keeps CPU use sane without hurting responsiveness.
        time.sleep_ms(2)


if __name__ == "__main__":
    run()
