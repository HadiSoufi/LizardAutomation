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
update_delay = float(config.get('Core', 'Update time (seconds)'))
dimmer_ips = config.get('Core', 'Dimmers').split(', ')

latitude = float(config.get('Timezone', 'Latitude'))
longitude = float(config.get('Timezone', 'Longitude'))
change_hours = float(config.get('Timezone', 'Fade time (hours)'))

send_texts = config.get('SMS', 'Send texts') == 'True'
phone_number = config.get('SMS', 'Phone number')
carrier = config.get('SMS', 'Carrier')

# Initialize dimmers
dimmers = [SmartDimmer(ip) for ip in dimmer_ips]

# Timezone
fade_time = timedelta(hours=change_hours)                               # Convert change_hours to a datetime object
sun_data = Sun(latitude, longitude)                                     # Sunrise/sunset from latitude/longitude
tz_name = TimezoneFinder().timezone_at(lng=longitude, lat=latitude)     # Timezone calculated from provided lat/long
tz = ZoneInfo(tz_name)                                                  # Timezone object from tz_name

# SMS
CARRIERS = {                                                            # List of mobile carrier gateway addresses.
    "att": "mms.att.net",                                               # If you don't see yours here, check:
    "tmobile": "tmomail.net",                                 # https://en.wikipedia.org/wiki/SMS_gateway#Email_clients
    "verizon": "vtext.com",
    "sprint": "messaging.sprintpcs.com",
    "boost": "smsmyboostmobile.com",
    "cricket": "sms.cricketwireless.net",
    "uscellular": "email.uscc.net"
}

carrier = ''.join(c for c in carrier if c.isalnum()).lower()            # Sanitize user setting
recipient = phone_number + "@" + CARRIERS[carrier]                      # Create recipient string
text_email = "lizardautomator@gmail.com"                                # Feel free to replace with your own email
text_password = "pven okhn kbmv wvmh"                                   # https://tinyurl.com/3svawyjn
email_host_name = "smtp.gmail.com"                                      # Only change if not using gmail

last_text_time = None


# Main loop
async def main():
    last_brightness = -1
    while True:
        # Using time of day, sunrise, and sunset (in local timezone)- find target dimmer brightness
        now = datetime.now(tz)
        sunrise = sun_data.get_local_sunrise_time(now, tz) - fade_time
        sunset = sun_data.get_local_sunset_time(now, tz) + fade_time

        # Account for suntime bug- sometimes sunset returns yesterday's sunset
        if sunset < sunrise:
            sunset += timedelta(1)

        brightness = calc_brightness(now, sunrise, sunset)

        # Update dimmers if brightness changed
        if brightness != last_brightness:
            last_brightness = brightness
            await set_brightness(brightness)

        # Delay until next update
        await asyncio.sleep(update_delay)


# Convert current time of day to an int (0-100), using sunrise/sunset and a fade time to blend.
def calc_brightness(now, sunrise, sunset):
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


# Set brightness on all switches
async def set_brightness(brightness):
    for i, dimmer in enumerate(dimmers):
        try:
            # Must be called before any calls to the dimmer
            await dimmer.update()

            if brightness == 0:
                await dimmer.turn_off()
            else:
                await dimmer.turn_on()
                await dimmer.set_brightness(brightness)

        except kasa.exceptions.SmartDeviceException as err:
            print(str(err))
            logging.warning("Lost connection with dimmer " + str(i) + ".\n\t" + str(err))
            send_text("Dimmer not responding, but server is running. Dimmer unplugged, bad IP, or hardware failure.")
        except Exception as err:
            print(str(err))
            logging.warning("Unknown error: " + str(i) + ".\n\t" + str(err))
            send_text("Lighting script is experiencing an unknown error\n\t" + str(err))
        else:
            continue


# Texting service. Works by sending an email to your carrier's gateway address, which is then forwarded as a text.
def send_text(message):
    if send_texts:
        try:
            server = smtplib.SMTP(email_host_name, 587)
            global last_text_time
            if (last_text_time is None
                    or datetime.now() - last_text_time >= timedelta(hours=2)):
                server.starttls()
                server.login(text_email, text_password)
                server.sendmail(text_email, recipient, message)
                last_text_time = datetime.now()
        except Exception as e:
            logging.error("Unable to send text: " + str(e))
    else:
        logging.warning(message)


if __name__ == "__main__":
    asyncio.run(main())
