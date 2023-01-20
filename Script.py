import asyncio
import pytz
import kasa
from suntime import Sun, SunTimeException
from kasa import SmartStrip
from kasa import SmartDimmer
from enum import Enum
from datetime import datetime
from datetime import timedelta

# Simple enum for code clarity
class DayState(Enum):
    night = 1
    sunrise = 2
    day = 3
    sunset = 4

# CONFIG
sun_data = Sun(35.227085, -80.843124)   # Use your latitude/longitude here. Very different timezones will cause errors
change_hours = 2                        # Number of hours for sunrise/sunset
ping_delay = 1                          # Amount of time to wait between running each loop. Higher values lead to increased smoothness during sunrise/sunset
strip = SmartStrip("192.168.1.160")     # Reference to actual strip
dimmer = SmartDimmer("192.168.1.161")   # Reference to actual dimmer

# See bottom line
async def main():
    while True:
        try:
            # Must be called before any other API calls
            await strip.update()
            await dimmer.update()
            
            # Gather individual plugs
            heat = strip.children[0]
            uvb = strip.children[1]
            plant = strip.children[2]

            # Get time of day and sunrise/set times in local timezone
            sunrise = sun_data.get_sunrise_time().astimezone()
            sunset = sun_data.get_sunset_time().astimezone()
            now = datetime.now().astimezone()

            # Calculate the state of day
            if now > sunrise and now < sunset:
                if now < sunrise + timedelta(hours=change_hours):
                    day_state = DayState.sunrise
                elif now > sunset - timedelta(hours=change_hours):
                    day_state = DayState.sunset
                else:
                    day_state = DayState.day
            else:
                day_state = DayState.night

            # Turn everything off at night
            if day_state == DayState.night:
                await dimmer.turn_off()
                await uvb.turn_off()
                await plant.turn_off()

            # Turn everything on during the day
            elif day_state == DayState.day:
                await dimmer.turn_on()
                await dimmer.set_brightness(100)
                await uvb.turn_on()
                await plant.turn_on()

            # Slowly dim the bulbs at sunrise
            elif day_state == DayState.sunrise:
                await dimmer.turn_on()
                await uvb.turn_on()
                await plant.turn_on()

                diff = now - sunrise
                brightness = diff / timedelta(hours=change_hours)
                await dimmer.set_brightness(brightness)

            # Slowly dim the bulbs at sunset
            elif day_state == DayState.sunset:
                await dimmer.turn_on()
                await uvb.turn_on()
                await plant.turn_on()

                diff = sunset - now
                brightness = diff / timedelta(hours=change_hours)
                await dimmer.set_brightness(brightness)
        
        # Exception handling. Most commonly caused by hardware or network issue.
        except asyncio.CancelledError as err:
            print(err)     
        except kasa.exceptions.SmartDeviceException as err:
            print(err)   
        finally:
            await asyncio.sleep(ping_delay)

# This is running in a jupyter notebook. For standalone, a different technique must be used
await main()
