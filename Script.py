#!/usr/bin/env python3

import asyncio
import kasa
import smtplib
import configparser
import logging
from kasa import SmartDimmer
from datetime import datetime
from datetime import timedelta
from suntime import Sun
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo

logging.basicConfig(filename='log.log', encoding='utf-8')

config = configparser.ConfigParser()
config.read("config.ini")

# Load from config.ini
ping_delay = int(config.get('Core', 'Update time'))
dimmer_ips = config.get('Core', 'Dimmers').split(', ')

latitude = float(config.get('Timezone', 'Latitude'))
longitude = float(config.get('Timezone', 'Longitude'))
change_hours = int(config.get('Timezone', 'Fade time'))

send_texts = config.get('SMS', 'Send texts') == 'True'
phone_number = config.get('SMS', 'Phone number')
carrier = config.get('SMS', 'Carrier')

# Initialize dimmers
dimmers = [SmartDimmer(ip) for ip in dimmer_ips]
# 192.168.1.161, 192.168.1.188

# Timezone
fade_time = timedelta(hours=change_hours)               # Convert change_hours to a datetime object
sun_data = Sun(latitude, longitude)                     # Get sunrise/sunset data from provided latitude/longitude
tz_name = TimezoneFinder().timezone_at(lng=longitude, lat=latitude)     # Timezone calculated from provided lat/long
tz = ZoneInfo(tz_name)                                  # Timezone object from tz_name

# SMS
CARRIERS = {                                            # List of mobile carrier gateway addresses.
    "att": "mms.att.net",                               # If you don't see yours here, check:
    "tmobile": "tmomail.net",                           # https://en.wikipedia.org/wiki/SMS_gateway#Email_clients
    "verizon": "vtext.com",
    "sprint": "messaging.sprintpcs.com",
    "boost": "smsmyboostmobile.com",
    "cricket": "sms.cricketwireless.net",
    "uscellular": "email.uscc.net"
}

carrier = ''.join(c for c in carrier if c.isalnum()).lower()
recipient = phone_number + "@" + CARRIERS[carrier]
text_email = "lizardautomator@gmail.com"                # Feel free to replace with your own email
text_password = "pven okhn kbmv wvmh"                   # App password for gmail- https://tinyurl.com/3svawyjn
server = smtplib.SMTP("smtp.gmail.com", 587)  # Replace this with the correct email client if not using gmail
last_text_time = None


# Main event loop
async def main():
    while True:
        # Validate dimmers
        if not await update_dimmers():
            continue

        # Get time of day, sunrise, and sunset in local timezone
        now = datetime.now(tz)
        sunrise = sun_data.get_local_sunrise_time(now, tz)
        sunset = sun_data.get_local_sunset_time(now, tz)

        # Calculate & set bulb brightness
        brightness = bulb_brightness(now, sunrise, sunset)
        if brightness == 0:
            await turn_off()
        elif brightness == 100:
            await turn_on()
        else:
            await set_brightness(brightness)

        # Delay between iterations
        await asyncio.sleep(ping_delay)


# Texting service. Works by sending an email to your carrier's gateway address, which is then forwarded as a text.
def send_text(message):
    if send_texts:
        try:
            global last_text_time
            if (last_text_time is None
                    or datetime.now() - last_text_time >= timedelta(hours=2)):
                server.starttls()
                server.login(text_email, text_password)
                server.sendmail(text_email, recipient, message)
                last_text_time = datetime.now()
        except Exception as e:
            logging.error("Unable to send text: " + e)
    else:
        print(message)


# Turn on all switches
async def turn_on():
    try:
        for dimmer in dimmers:
            await dimmer.turn_on()
            await dimmer.set_brightness(100)
    except asyncio.CancelledError:
        print("Operation cancelled.")
    except kasa.exceptions.SmartDeviceException as err:
        print(err)


# Set brightness on all switches
async def set_brightness(brightness):
    try:
        for dimmer in dimmers:
            await dimmer.turn_on()
            await dimmer.set_brightness(brightness)
    except asyncio.CancelledError:
        print("Operation cancelled.")
    except kasa.exceptions.SmartDeviceException as err:
        print(err)


# Turn off all switches
async def turn_off():
    try:
        for dimmer in dimmers:
            await dimmer.turn_off()
    except asyncio.CancelledError:
        print("Operation cancelled.")
    except kasa.exceptions.SmartDeviceException as err:
        print(err)


# Must be called before doing any operations on the dimmers
async def update_dimmers():
    for dimmer, i in enumerate(dimmers):
        try:
            await dimmer.update()
        except asyncio.CancelledError:
            print("Operation cancelled.")
            return False
        except kasa.exceptions.SmartDeviceException as err:
            logging.warning("Lost connection with dimmer " + str(i))
            send_text("Dimmer not responding, but server is running. Dimmer unplugged, bad IP, or hardware failure.")
            return False
        else:
            return True


# For testing
def debug():
    now = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    increment_hours = 1/60

    while True:
        # Update current time
        now += timedelta(hours=increment_hours)

        # Get time of day, sunrise, and sunset in local timezone
        sunrise = sun_data.get_local_sunrise_time(now, tz)
        sunset = sun_data.get_local_sunset_time(now, tz)

        val = ''
        brightness = bulb_brightness(now, sunrise, sunset)
        if brightness == 0:
                val = 'Night'
        elif brightness == 100:
                val = 'Day'
        else:
            if now < (sunrise + fade_time):
                val = 'Sunrise: ' + str(brightness)
            # Sunset
            elif now > (sunset - fade_time):
                val = 'Sunset: ' + str(brightness)
        print(val)


# Calculate the bulb's brightness based on time of day
def bulb_brightness(now, sunrise, sunset):
    if sunrise < now < sunset:
        # Sunrise
        if now < (sunrise + fade_time):
            return int(100 * (now - sunrise) / fade_time)
        # Sunset
        elif now > (sunset - fade_time):
            return int(100 * (sunset - now) / fade_time)
        # Day
        else:
            return 100
    # Night
    else:
        return 0


if __name__ == "__main__":
    asyncio.run(main())
