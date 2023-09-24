#!/usr/bin/env python3

import asyncio
import kasa
from kasa import SmartStrip
from kasa import SmartDimmer
from datetime import datetime
from datetime import timedelta
from suntime import Sun
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo

# CONFIG
latitude = 35.227085                                    # Timezone latitude
longitude = -80.843124                                  # Timezone longitude
change_hours = 2                                        # Number of hours for sunrise/sunset
ping_delay = 1                                          # Amount of time in seconds to wait between updates
strip = SmartStrip("192.168.1.160")                     # Smart strip
dimmers = [[SmartDimmer("192.168.1.161"), 1],           # First number is dimmer ip, second is position on strip
           [SmartDimmer("192.168.1.188"), 2],
           [SmartDimmer("192.168.1.187"), 3]]

# GLOBAL
fade_time = timedelta(hours=change_hours)               # Convert change_hours to a datetime object
sun_data = Sun(latitude, longitude)                     # Get sunrise/sunset data from provided latitude/longitude
tz_name = TimezoneFinder().timezone_at(lng=longitude, lat=latitude)     # Timezone calculated from provided lat/long
tz = ZoneInfo(tz_name)                                  # Timezone object from tz_name


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
        match brightness:
            case 0:
                await turn_off()
            case 100:
                await turn_on()
            case _:
                await set_brightness(brightness)

        # Delay between iterations
        await asyncio.sleep(ping_delay)


# Turn on all switches
async def turn_on():
    try:
        for dimmer in dimmers:
            await dimmer[0].update()
            await dimmer[0].turn_on()
            await dimmer[0].set_brightness(100)
    except asyncio.CancelledError:
        print("Operation cancelled.")
    except kasa.exceptions.SmartDeviceException as err:
        print(err)


# Set brightness on all switches
async def set_brightness(brightness):
    try:
        for dimmer in dimmers:
            await dimmer[0].update()
            await dimmer[0].turn_on()
            await dimmer[0].set_brightness(brightness)
    except asyncio.CancelledError:
        print("Operation cancelled.")
    except kasa.exceptions.SmartDeviceException as err:
        print(err)


# Turn off all switches
async def turn_off():
    try:
        for dimmer in dimmers:
            await dimmer[0].turn_off()
    except asyncio.CancelledError:
        print("Operation cancelled.")
    except kasa.exceptions.SmartDeviceException as err:
        print(err)


# Must be called before doing any operations on the dimmers
async def update_dimmers():
    # Validate power strip first
    try:
        await strip.update()
    except asyncio.CancelledError:
        print("Operation cancelled.")
        return False
    except kasa.exceptions.SmartDeviceException as err:
        print("Error connecting to Smart Strip: " + repr(err))
        print("Make sure the device is connected to the network, or check the IP.")
        return False

    for dimmer in dimmers:
        i = dimmer[1] - 1

        try:
            await dimmer[0].update()
        except asyncio.CancelledError:
            print("Operation cancelled.")
            return False
        except kasa.exceptions.SmartDeviceException as err:
            if strip.children[i].is_on:
                print("Error connecting to Smart Dimmer: " + repr(err))
                print("Make sure the device is connected to the network, or check the IP.")
            else:
                print("Error connecting to Smart Dimmer. Attempting to resolve automatically.")
                await strip.children[i].turn_on()
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
        match brightness:
            case 0:
                val = 'Night'
            case 100:
                val = 'Day'
            case _:
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
