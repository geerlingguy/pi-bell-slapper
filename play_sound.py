#!/usr/bin/env python3

# The sound player script.

from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
import argparse


# Play the sound.
def play_the_sound(file='./ding.wav'):
    # Define optional command line argument.
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="File")

    # Get arguments from command line (if supplied).
    args = parser.parse_args()
    sound_file = args.file if bool(args.file) else file

    # Play the sound.
    pygame.mixer.init()
    sound = pygame.mixer.Sound(sound_file)
    playing = sound.play()
    while playing.get_busy():
        pygame.time.delay(100)


if __name__ == '__main__':
    # This script is being executed directly. Play the sound right away!
    play_the_sound()
