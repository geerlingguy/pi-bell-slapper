#!/usr/bin/env python3

# The bell slapper script.

from time import sleep
import argparse
import RPi.GPIO as GPIO


# Slap the bell.
def slap_the_bell():
    try:
        # GPIO Pin where solenoid control circuit is connected.
        solenoid_pin = 4

        # Define optional command line arguments.
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--count", help="Count (how many dings)")
        parser.add_argument("-i", "--interval", help="Interval between dings")

        # Get arguments from command line (if supplied).
        args = parser.parse_args()
        ding_count = int(args.count) if bool(args.count) else int('1')
        ding_interval = float(args.interval) if bool(args.interval) else float('1.0')

        # Don't allow dinging faster than every 0.05 seconds.
        if ding_interval < 0.05:
            ding_interval = float('0.05')
            print("Interval was reset to 0.05 to protect the circuit.")

        # Define the Pin numbering type and define Servo Pin as output pin.
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(solenoid_pin, GPIO.OUT)

        # Bell slap loop.
        while (ding_count > 0):
            GPIO.output(4, GPIO.HIGH)
            sleep(0.01)
            GPIO.output(4, GPIO.LOW)
            sleep(ding_interval)
            ding_count -= 1

    except KeyboardInterrupt:
        print("User stopped script during execution.")

    finally:
        try:
            GPIO.cleanup()

        except NameError:
            pass


if __name__ == '__main__':
    # This script is being executed directly. Slap the bell right away!
    slap_the_bell()
