#!/usr/bin/env python3

import asyncio
import pytz
import kasa
from suntime import Sun, SunTimeException
from kasa import SmartStrip
from kasa import SmartDimmer
from enum import Enum
from datetime import datetime
from datetime import timedelta

# CONFIG
latitude = 35.227085                            # Timezone latitude
longitude = -80.843124                          # Timezone longitude
change_hours = 2                                # Number of hours for sunrise/sunset
ping_delay = 1                                  # Amount of time in seconds to wait between running each loop. Higher values lead to increased smoothness during sunrise/sunset
strip = SmartStrip("192.168.1.160")             # Smart strip
dimmers = [[SmartDimmer("192.168.1.161"), 1],   # Dimmers to sync to day/night. 
           [SmartDimmer("192.168.1.187"), 3]]    # First number is dimmer ip, second is position on strip.
heat = SmartDimmer("192.168.1.188")             # Heat dimmer is kept separate for temperature control.

fade_time = timedelta(hours = change_hours)     # Convert change_hours to a datetime object
sun_data = Sun(latitude, longitude)             # Get sunrise/sunset data from provided latitude/longitude

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
    await heat.turn_off()

# Validate dimmers
async def update_dimmers():
    for dimmer in dimmers:
        i = dimmer[1] - 1
        
        try:
            await dimmer[0].update()
        except asyncio.CancelledError as err:
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
    
# Validate dimmers
async def update_heat():
    try:
        await heat.update()
    except asyncio.CancelledError as err:
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
        # Delay between iterations
        await asyncio.sleep(ping_delay)
        
        # Get time of day, sunrise, and sunset in local timezone
        sunrise = sun_data.get_sunrise_time().astimezone()
        sunset = sun_data.get_sunset_time().astimezone()
        now = datetime.now().astimezone()
        
        # Validate power strip
        try:
            await strip.update()
        except asyncio.CancelledError as err:
            print("Operation cancelled.")    
            continue
        except kasa.exceptions.SmartDeviceException as err:
            print("Error connecting to Smart Strip: " + repr(err))
            print("Make sure the device is connected to the network, or check the IP.")
            continue
        
        # Validate dimmers
        if not await update_dimmers():
            continue
        if not await update_heat():
            continue
            
        # Update lights
        try:
            if now > sunrise and now < sunset:
                # Sunrise
                if now < sunrise + fade_time:
                    await set_brightness(int ((sunset - now) / fade_time))
                # Sunset
                elif now > sunset - fade_time:
                    await set_brightness(int ((sunset - now) / fade_time))
                # Day
                else:
                    await turn_on()
            # Night
            else:
                await turn_off()
        except asyncio.CancelledError as err:
            print("Operation cancelled.")
            continue
        except kasa.exceptions.SmartDeviceException as err:
            print(err)
            continue

# if in Jupyter, "await main" will be fine
if __name__ == "__main__":
    asyncio.run(main())
