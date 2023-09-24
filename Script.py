#!/usr/bin/env python3

import asyncio
import kasa
from kasa import SmartStrip
from kasa import SmartDimmer
from datetime import datetime
from datetime import timedelta
from suntime import Sun
from timezonefinder import TimezoneFinder
from pytz import timezone

# CONFIG
latitude = 35.227085                                    # Timezone latitude
longitude = -80.843124                                  # Timezone longitude
change_hours = 2                                        # Number of hours for sunrise/sunset
ping_delay = 1                                          # Amount of time in seconds to wait between running each loop.
strip = SmartStrip("192.168.1.160")                     # Smart strip
dimmers = [[SmartDimmer("192.168.1.161"), 1],           # First number is dimmer ip, second is position on strip.
           [SmartDimmer("192.168.1.188"), 2],
           [SmartDimmer("192.168.1.187"), 3]]
heat = SmartDimmer("192.168.1.188")                     # Heat dimmer is kept separate for temperature control. Unused.

# GLOBAL
fade_time = timedelta(hours=change_hours)               # Convert change_hours to a datetime object
sun_data = Sun(latitude, longitude)                     # Get sunrise/sunset data from provided latitude/longitude
tz = timezone(TimezoneFinder().timezone_at(lng=longitude, lat=latitude))


# Turn on all switches
async def turn_on():
    for dimmer in dimmers:
        await dimmer[0].update()
        await dimmer[0].turn_on()
        await dimmer[0].set_brightness(100)


# Set brightness on all switches
async def set_brightness(brightness):
    for dimmer in dimmers:
        await dimmer[0].update()
        await dimmer[0].turn_on()
        await dimmer[0].set_brightness(brightness)


# Turn off all switches
async def turn_off():
    for dimmer in dimmers:
        await dimmer[0].turn_off()
    # await heat.turn_off()


# Validate dimmers
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


# Validate heat bulb specifically- unused
async def update_heat():
    try:
        await heat.update()
    except asyncio.CancelledError:
        print("Operation cancelled.")
        return False
    except kasa.exceptions.SmartDeviceException as err:
        if strip.children[1].is_on:
            print("Error connecting to Smart Dimmer: " + repr(err))
            print("Make sure the device is connected to the network, or check the IP.")
        else:
            print("Error connecting to Smart Dimmer. Attempting to resolve automatically.")
            await strip.children[1].turn_on()
        return False
    else:
        return True


# Main event loop
async def main():
    while True:
        # Validate dimmers
        if not await update_dimmers():
            continue

        # Get time of day, sunrise, and sunset in local timezone
        now = datetime.now().astimezone(tz)
        sunrise = sun_data.get_sunrise_time(now).astimezone(tz)
        sunset = sun_data.get_sunset_time(now).astimezone(tz)

        # Update lights
        try:
            if sunrise < now < sunset:

                # Calculate time of day to start fading
                sunrise_fade = (sunrise + fade_time).time()
                sunset_fade = (sunset - fade_time).time()

                # Sunrise
                if now.time() < sunrise_fade:
                    await set_brightness(int(100 * (now - sunrise) / fade_time))
                # Sunset
                elif now.time() > sunset_fade:
                    await set_brightness(int(100 * (sunset - now) / fade_time))
                # Day
                else:
                    await turn_on()
            # Night
            else:
                await turn_off()
        except asyncio.CancelledError:
            print("Operation cancelled.")
            continue
        except kasa.exceptions.SmartDeviceException as err:
            print(err)
            continue

        # Delay between iterations
        await asyncio.sleep(ping_delay)


# For testing
def debug():
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    print(now)
    increment_hours = 1/60

    while True:
        # Update current time
        now += timedelta(hours=increment_hours)
        now_format = now.astimezone(tz)

        # Get time of day, sunrise, and sunset in local timezone
        sunrise = sun_data.get_sunrise_time(now).astimezone(tz)
        sunset = sun_data.get_sunset_time(now).astimezone(tz)

        sunrise_fade = (sunrise + fade_time).time()
        sunset_fade = (sunset - fade_time).time()

        if sunrise < now_format < sunset:
            # Sunrise
            if now_format.time() < sunrise_fade:
                val = 'Sunrise: ' + str(int(100 * (now_format - sunrise) / fade_time))
            # Sunset
            elif now_format.time() > sunset_fade:
                val = 'Sunset: ' + str(int(100 * (sunset - now_format) / fade_time))
            # Day
            else:
                val = 'Day'
        # Night
        else:
            val = 'Night'

        print(val)


# debug()

if __name__ == "__main__":
    asyncio.run(main())
