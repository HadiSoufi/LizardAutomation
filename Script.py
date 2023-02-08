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
latitude = 35.227085                    # Timezone latitude
longitude = -80.843124                 # Timezone longitude
change_hours = 2                        # Number of hours for sunrise/sunset
ping_delay = 1                          # Amount of time in seconds to wait between running each loop. Higher values lead to increased smoothness during sunrise/sunset
strip = SmartStrip("192.168.1.160")     # Strip object
dimmer = SmartDimmer("192.168.1.161")   # Dimmer object

fade_time = timedelta(hours = change_hours)     # Convert change_hours to a datetime object
sun_data = Sun(latitude, longitude)             # Convert change_hours to a datetime object

# Turn on all switches
async def turn_on():
    await dimmer.turn_on()
    await dimmer.set_brightness(100)
    await uvb.turn_on()
    await plant.turn_on()

# Set brightness on dimmer switches, turn others on
async def set_brightness(brightness):
    await dimmer.turn_on()
    await dimmer.set_brightness(brightness)
    await uvb.turn_on()
    await plant.turn_on()
    
# Turn off all switches    
async def turn_off():
    await dimmer.turn_off()
    await uvb.turn_off()
    await plant.turn_off()

# Update all smart devices
async def update():
    await strip.update()
    await dimmer.update()
    
# Main event loop
async def main():
    while True:
        try:
            # Must be called before any other API calls
            update()
            
            # Gather individual plugs
            heat = strip.children[0]
            uvb = strip.children[1]
            plant = strip.children[2]

            # Get time of day, sunrise, and sunset in local timezone
            sunrise = sun_data.get_sunrise_time().astimezone()
            sunset = sun_data.get_sunset_time().astimezone()
            now = datetime.now().astimezone()

            # Calculate the state of day
            if now > sunrise and now < sunset:
                # Sunrise
                if now < sunrise + fade_time:
                    set_brightness(int ((sunset - now) / fade_time))
                # Sunset
                elif now > sunset - fade_time:
                    set_brightness(int ((sunset - now) / fade_time))
                # Day
                else:
                    turn_on()
            # Night
            else:
                turn_off()
        
        # Exception handling. Most commonly caused by hardware or network issue.
        except asyncio.CancelledError as err:
            print(err)     
        except kasa.exceptions.SmartDeviceException as err:
            print(err)   
        finally:
            await asyncio.sleep(ping_delay)
            
# if in Jupyter, "await main" will be fine
if __name__ == "__main__":
    asyncio.run(main())
