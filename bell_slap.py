#!/usr/bin/env python3

# The bell slapper script.
# Adapted from: https://gist.github.com/meub/c3833921a3a45a3ec392d9962313b68e

from time import sleep

# Try importing the GPIO library.
try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    print("RPi module not found. Ignoring bell slaps.\n")


# Slap the bell.
def slap_the_bell():
    try:
        # Set up GPIO
        servo_pin = 21  # GPIO Pin where servo is connected
        GPIO.setmode(GPIO.BCM)

        # Define the Pin numbering type and define Servo Pin as output pin
        GPIO.setup(servo_pin, GPIO.OUT)
        p = GPIO.PWM(servo_pin, 50)  # PWM channel at 50 Hz frequency
        p.start(0)  # Zero duty cycle initially

        # Slap the bell.
        sleep(0.4)
        p.ChangeDutyCycle(12)
        sleep(0.4)
        p.ChangeDutyCycle(9)
        sleep(0.25)
        p.ChangeDutyCycle(12)
        sleep(0.4)

    except KeyboardInterrupt:
        print("User stopped script during execution.")

    except NameError:
        print("GPIO not defined. Ignoring bell slap.\n")

    finally:
        try:
            GPIO.cleanup()

        except NameError:
            pass


if __name__ == '__main__':
    # This script is being executed directly. Slap the bell right away!
    slap_the_bell()
