#!/usr/bin/env python

# The bell slapper script.
# Adapted from: https://gist.github.com/meub/c3833921a3a45a3ec392d9962313b68e

import RPi.GPIO as GPIO
from time import sleep

try:
  # Set up GPIO
  servo_pin = 21 # GPIO Pin where servo is connected
  GPIO.setmode(GPIO.BCM)

  # Define the Pin numbering type and define Servo Pin as output pin
  GPIO.setup(servo_pin, GPIO.OUT)
  p = GPIO.PWM(servo_pin, 50) # PWM channel at 50 Hz frequency
  p.start(0) # Zero duty cycle initially

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

except:
  print("Couldn't use GPIO for some reason.")

finally:
  # End GPIO session.
  GPIO.cleanup()
