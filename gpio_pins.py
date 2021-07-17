#!/usr/bin/env python3

# GPIO interactions

from time import sleep

# Try importing the GPIO library.
try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    print("RPi module not found. Ignoring GPIO interactions.\n")


# Slap the bell.
def led_up():
    try:
        # GPIO Pin where LEDs' connected.
        led_pins = [37, 38, 40]

        # Define the Pin numbering type and define LED Pins as output pins.
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(led_pins, GPIO.OUT)

        # LED sequence
        for led in led_pins:
            GPIO.output(led, GPIO.HIGH)
            sleep(0.1)
            GPIO.output(led, GPIO.LOW)

    except KeyboardInterrupt:
        print("User stopped script during execution.")

    except NameError:
        print("GPIO not defined. Ignoring LEDs sequence.\n")

    finally:
        try:
            GPIO.cleanup()

        except NameError:
            pass


if __name__ == '__main__':
    # This script is being executed directly. leds go brr!
    led_up()