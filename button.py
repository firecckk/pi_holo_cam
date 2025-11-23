import RPi.GPIO as GPIO

BUTTON_PINS = [16, 20, 21]
PULLUP_PIN = 12

def gpio_button_init(button_callback):
    # init gpio
    GPIO.setmode(GPIO.BCM)
    
    GPIO.setup(PULLUP_PIN, GPIO.OUT)
    GPIO.output(PULLUP_PIN, GPIO.HIGH)

    for pin in BUTTON_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_OFF)

        GPIO.add_event_detect(pin, GPIO.FALLING, 
                         callback=button_callback, 
                         bouncetime=60)