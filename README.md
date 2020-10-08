# Raspberry Pi Bell Slapper

[![CI](https://github.com/geerlingguy/pi-bell-slapper/workflows/CI/badge.svg)](https://github.com/geerlingguy/pi-bell-slapper/actions?query=workflow%3ACI)

(Insert really amazing picture of the horrific contraption I build at some later time.)

Why? I need a Raspberry Pi to slap a bell in response to a particular trigger.

In my case, it's for a radiothon. When a nonprofit community radio station gets a phone call, you can hear the phone in the background. When they get an online donation, you hear nothing.

Something is better than nothing, so I made this project, which slaps a bell upon a triggering condition.

## How is the bell slapped?

I'm glad you asked.

I bought a set of [MG90S Micro Servos](https://amzn.to/2I6sZSC). The Pi tells the servo to go, the servo hits the bell with a little armature, and there you have it.

## What kind of bell does it slap?

I'm currently slapping a boring old call bell. [This call bell](https://amzn.to/3iCUL5F). But any bell you could mount to be slapped would work.

## How do I slap a bell?

Well now, here's where it gets interesting. I thought I'd share all the code and tell you how it's done. That's why you're reading this, isn't it?

  1. Clone this repository to your Pi.
  1. Plug in the following wires on the servo motor:

     1. Red wire to 5V power (pin 4)
     1. Brown wire to ground (pin 6)
     1. Orange wire to GPIO 21 (pin 40)

  1. Run the command `./bell_slap.py` in this directory.
  1. Wait a second, and you'll see the motor spin, then reverse back to its original position.

> Note: The servo's wires come preinstalled into a 3-pin dupont female connector. You can use a tiny thing to pry up the release on the orange pin barrel connector, and slide that out. Then slide it into a separate 1-pin dupont female connector, and voila! You can then plug that orange wire directly into pin 40.

### But how do I really slap a bell?

Well... it's a little more complicated because to slap a real bell, you have to mount the servo motor to something solid, build a little armature to actually hit the bell, mount the bell so it doesn't move when it's slapped, and then power the Pi and build something on it that automatically runs the `./bell_slap.py` script.

I'll try to detail the whole process later, after I figure it out myself ;).

## How do I tie an email inbox to the bell slapper?

Well, now we're getting to the meat of it.

It's easy enough to slap a bell with your hand; there's no point in making a Raspberry Pi do it if you just want to slap the bell once or twice.

I built this project to monitor an email inbox. So I wrote a Python script, `email-check.py`. That python script does all the magic of translating "new email arrives" into "the bell has been resoundingly slapped".

To make this script work, you need to do two things on the Pi:

  1. Copy the `config.example.yml` file to a file named `config.yml`, and modify it with the email credentials for the account to be monitored.
  2. Run `pip install imapclient` to install the [IMAPClient Python library](https://imapclient.readthedocs.io/en/2.1.0/).

Then run `./email-check.py`, and prepare to be amazed! Or not, especially if it doesn't work.

## Were you inspired by anyone?

Of course I was inspired. You don't think I came up with all this on my own, did you? Alex Meub's [Office Bell Ringer](https://alexmeub.com/office-bell-ringer/) was my inspiration. Go read that post if you want to discover how I was inspired.

Why are you so interested in _my_ inspiration? Go find your own.

## Who are you?

I'm [Jeff Geerling](https://www.jeffgeerling.com), and I approve of this repository.
