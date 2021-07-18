#!/usr/bin/env python3

# GPIO interactions

from time import sleep

# Try importing the GPIO library.
try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    print("RPi module not found. Ignoring GPIO interactions.\n")


# LED sequences
def led_sequence(n):
    try:
        # GPIO Pin where LEDs' connected.
        led_pins = [37, 38, 40]
    
        # Define the Pin numbering type and define LED Pins as output pins.
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(led_pins, GPIO.OUT)

        if n == 1:
            for led in led_pins:
                GPIO.output(led, GPIO.HIGH)
                sleep(0.5)
                GPIO.output(led, GPIO.LOW)
                sleep(0.3)
            for led in reversed(led_pins):
                GPIO.output(led, GPIO.HIGH)
                sleep(0.5)
                GPIO.output(led, GPIO.LOW)
                sleep(0.3)
            GPIO.output(led_pins, GPIO.HIGH)
            sleep(0.3)
            GPIO.output(led_pins, GPIO.LOW)
            sleep(0.3)
            GPIO.output(led_pins, GPIO.HIGH)
            sleep(0.3)
            GPIO.output(led_pins, GPIO.LOW)
        elif n == 2:
            while True:
                GPIO.output(led_pins[37], GPIO.HIGH)
                sleep(0.3)
                GPIO.output(led_pins[37], GPIO.LOW)
                sleep(0.3)
        else:
            while True:
                GPIO.output(led_pins[38], GPIO.HIGH)
                sleep(0.3)
                GPIO.output(led_pins[38], GPIO.LOW)
                sleep(0.3)
        

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
    led_sequence()
