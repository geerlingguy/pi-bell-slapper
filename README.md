# Raspberry Pi Bell Slapper

_a.k.a. "The King of Ding"_

[![CI](https://github.com/geerlingguy/pi-bell-slapper/workflows/CI/badge.svg)](https://github.com/geerlingguy/pi-bell-slapper/actions?query=workflow%3ACI)

<img src="https://raw.githubusercontent.com/geerlingguy/pi-bell-slapper/master/images/bell-slapper-mark-1.jpeg" width="600" height="408" alt="Raspberry Pi Bell Slapper - Mark I" />

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

  1. Clone this repository to your Pi: `git clone https://github.com/geerlingguy/pi-bell-slapper.git`
  1. Run `python3 -m pip install RPi.GPIO` to install required dependencies.
  1. Plug in the following wires on the servo motor (see illustration below):

     1. Red wire to 5V power (pin 4)
     1. Brown wire to ground (pin 6)
     1. Orange wire to GPIO 21 (pin 40)

  1. Change into this directory (`cd pi-bell-slapper`) and run the command `./bell_slap.py`.
  1. Wait a second, and you'll see the motor spin, then reverse back to its original position.

Here's an illustration of the servo connections:

<img src="https://raw.githubusercontent.com/geerlingguy/pi-bell-slapper/master/images/servo-raspberry-pi-connections.jpeg" width="600" height="401" alt="Servo motor Pi connections" />

> Note: The servo's wires come preinstalled into a 3-pin dupont female connector. You can use a tiny thing to pry up the release on the orange pin barrel connector, and slide that out. Then slide it into a separate 1-pin dupont female connector, and voila! You can then plug that orange wire directly into pin 40.

### But how do I mount this contraption to _actually_ slap a bell?

Well... it's a little more complicated because to slap a real bell, you have to mount the servo motor to something solid, build a little armature to slap the bell, mount the bell so it doesn't move when slapped.

You can see my franken-build up at the top of this README. It ain't pretty, but she's got it where it counts.

Someday I hope to make a 'Mark II' version of the build that looks... not so janky.

## How do I tie email notifications to the bell slapper?

Well, now we're getting to the meat of it.

It's easy enough to slap a bell with your hand; there's no point in making a Raspberry Pi do it if you just want to slap the bell once or twice.

I built this project to monitor an email inbox. So I wrote a Python script, `email-check.py`. That python script does all the magic of translating "new email arrives" into "the bell has been resoundingly slapped".

To make this script work, you need to do two things on the Pi:

  1. Copy the `config.example.yml` file to a file named `config.yml`, and modify it with the email credentials for the account to be monitored.
  2. Run `python3 -m pip install imapclient pyyaml` to install required dependencies.

Then run `./email-check.py`, and prepare to be amazed! Or not, especially if it doesn't work.

> You might also need to install Pip, if you get an error on the `python3 -m pip` command. To do that, run `sudo apt install -y python3-pip`.

### How do I continuously check the email inbox?

Well now we're really getting somewhere useful!

For now, I'm just using cron. Fire up the ol' crontab editor (`crontab -l`) and add the following line:

```
* * * * * /home/pi/pi-bell-slapper/email_check.py
```

Then every minute the script will run!

> Note: If you have any errors, cron will email them to localhost (make sure you have something like `postfix` and `mailutils` installed to catch and read those emails). Other cron output goes into the syslog (check `/var/log/syslog`).

For my own Pi model A+, the WiFi chipset I used went to sleep after a minute, causing lookups to fail. So I had to [follow my own directions to stop the thing from sleeping](https://www.jeffgeerling.com/blogs/jeff-geerling/edimax-ew-7811un-tenda-w311mi-wifi-raspberry-pi), and it worked a lot better.

## Were you inspired by anyone?

Of course I was inspired. You don't think I came up with all this on my own, did you? Alex Meub's [Office Bell Ringer](https://alexmeub.com/office-bell-ringer/) was my inspiration. Go read that post if you want to discover how I was inspired.

Why are you so interested in _my_ inspiration? Go find your own.

## Who are you?

I'm [Jeff Geerling](https://www.jeffgeerling.com), and I approve of this repository.
