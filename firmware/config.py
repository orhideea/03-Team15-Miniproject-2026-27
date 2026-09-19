#GPIO 1-4 control the motor
STEP_PINS = (1, 2, 3, 4)  

# motor rotation sequence set up
# coil order: orange -> pink -> yellow -> blue 
STEP_SEQUENCE = (
    (1, 0, 0, 0),  
    (0, 1, 0, 0),  
    (0, 0, 1, 0),  
    (0, 0, 0, 1),  
)

# one full revolution
STEPS_PER_REV = 2048 

# 180º step set-up
SWEEP_STEPS = 1024  


# GPIO LED pin set up
LED_RED = 7
LED_BLUE = 8
LED_GREEN = 9
PWM_FREQ = 1000  

# controls brightness
PULSE_PERIOD_MS = 1000 


BTN_SELECT = 5  #timer presets
BTN_START = 6  #start/stop timer control

#debounce time setup 
DEBOUNCE_MS = 50
LONG_PRESS_MS = 1000


PRESETS_MIN = (15, 20, 25, 30)
