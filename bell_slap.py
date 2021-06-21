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
        # GPIO Pin where solenoid control circuit is connected.
        solenoid_pin = 4

        # Define the Pin numbering type and define Servo Pin as output pin.
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(solenoid_pin, GPIO.OUT)

        # Slap the bell.
        GPIO.output(4, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(4, GPIO.LOW)

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
