from machine import Pin, PWM
import time
import config


# increasing PWM = brighter LED
COMMON_ANODE = False


# setting up states with LEDs
_STATE_TABLE = {
    "select": ("blue", True), #pulse
    "running": ("green", False), # no pulse
    "paused": ("green", True), # pulse
    "expired": ("red", True), # pulse
}

_channels = {}  #color name is PWM object
_state = "select"  #current state name


#create PWM outputs
def init():
    global _channels
    _channels = {
        "red": PWM(Pin(config.LED_RED), freq=config.PWM_FREQ, duty_u16=0),
        "blue": PWM(Pin(config.LED_BLUE), freq=config.PWM_FREQ, duty_u16=0),
        "green": PWM(Pin(config.LED_GREEN), freq=config.PWM_FREQ, duty_u16=0),
    }
    off()

#state selection function
def set_state(name):
    global _state
    if name in _STATE_TABLE:
        _state = name

#called repeatedly from main loop to read millisecond clock 
def update():
    if not _channels:
        return

    color, pulsing = _STATE_TABLE[_state]
    level = _pulse_level() if pulsing else 1.0

    for name, pwm in _channels.items():
        pwm.duty_u16(_duty(level) if name == color else _duty(0.0))

#turns all three channcels off
def off():
    for pwm in _channels.values():
        pwm.duty_u16(_duty(0.0))
        
#pulsing from dark to bright to dark 
#cycle of 1 second 
def _pulse_level():
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
