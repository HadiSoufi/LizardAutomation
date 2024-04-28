# What this is
A simple script that automatically syncs some Kasa dimmers to a day/night cycle at a location of your choosing. I keep reptiles, so I use this to simulate a more natural environment in their enclosures than what off-the-shelf solutions provide. I run it on a Pi Zero W, but it should work basically anywhere as long as it's on the same network as your hardware.

# Forewarnings
* Not every bulb can dim- fluorescent UVB bulbs for instance cannot- so you may find your bulb is flickering or whining.
* The dimmer's networking component can fail silently. If you notice that your system simply stops working with no error messages in the log, you may want to try replacing your dimmer.

# Setup
**Requires Python 3.9 or greater and at least one Kasa Smart Dimmer**
1. Clone this repository into a folder with read/write access
2. Install requirements.txt
3. [Follow this guide to get your Kasa device information](https://python-kasa.readthedocs.io/en/latest/)
4. Modify the config file so that it accurately reflects your setup and needs
5. Run the script

# The Writeup
There are four solutions that currently exist for managing reptile lights.
1. ### Manual

   Turning all your bulbs on and off every day by hand is 100% free and you could create any day/night cycle you want. It also sucks.
2. ### Mechanical timers

   [Mechanical timers](https://www.amazon.com/GE-Mechanical-Intervals-Decorations-46211/dp/B07YQKNC4D/ref=sr_1_5?keywords=mechanical+outlet+timer&qid=1695593724&sr=8-5) are cheap, intuitive, and widely available, making them popular with beginners. They come with two major downsides- they're noisy, and they drift. You have to do a maintenance check every couple of months to keep up with seasonal daylight changes & fix drift, as well as whenever there's an outage.
3. ### Electrical timers

   [Electrical timers](https://www.amazon.com/Fosmon-Programmable-Seasonal-Portable-Aquarium/dp/B07HCQKRRY/ref=sr_1_6?keywords=outlet%2Btimer&qid=1695594132&sr=8-6&th=1) are very similar to mechanical timers, but use a chip to keep time. Nowadays, they're barely more expensive than mechanical timers, and totally silent. They're also less prone to drift, though it will still happen over time. Otherwise, they function identically and carry the same downsides. In my opinion, they're strictly better than mechanical timers, barring that some may have a slightly less intuitive user interface.
4. ### Smart plugs

   [Smart plugs](https://www.amazon.com/BN-LINK-Monitoring-Function-Compatible-Assistant/dp/B07CVPKD8Z/ref=sxin_14_pa_sp_search_thematic_sspa?content-id=amzn1.sym.1c86ab1a-a73c-4131-85f1-15bd92ae152d%3Aamzn1.sym.1c86ab1a-a73c-4131-85f1-15bd92ae152d&cv_ct_cx=outlet+timer&keywords=outlet+timer&pd_rd_i=B07CVPKD8Z&pd_rd_r=e67b4845-b45c-4157-b841-5e58270cb774&pd_rd_w=UkVWU&pd_rd_wg=v4H3c&pf_rd_p=1c86ab1a-a73c-4131-85f1-15bd92ae152d&pf_rd_r=YZVE1NQHJJXHBENVCX92&qid=1695594132&sbo=RZvfv%2F%2FHxDF%2BO5021pAnSA%3D%3D&sr=1-2-364cf978-ce2a-480a-9bb0-bdb96faa0f61-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9zZWFyY2hfdGhlbWF0aWM&psc=1) are a bit different. Because they're internet-enabled, they're completely immune to drift & resilient to power outages and, because they're fully electric, they're completely silent too. Many can be easily programmed to turn on and off at sunrise/sunset, and they can be dirt cheap. In some ways, these are an ideal solution for your average reptile keeper. The main downside is that there's no standardization- some use an app, some use a hub; some apps are good, some apps suck; and many apps require your phone to be on the same wifi network for scripting to work. They also tend to be shockingly easy to hack, and so can function as a backdoor into your home network. Finally, they're harder to setup than mechanical/electric timers, requiring you to install an app, connect the devices to your network, and configure the devices.

### My solution
I've used all of these solutions with my reptiles at various points, and I definitely favor smart plugs. However, I got tired of their issues, so I made my own solution. It uses Kasa brand smart devices, because, at time of writing, they have a great API and Python library that makes scripting super easy. Some advantages are-
* **No app:** No app means no reliance on any infrastructure other than my own. In today's world where any service can be killed at any moment, this provides me with tremendous peace of mind.
* **Robust:** If the power goes out, I can trust that everything will go back to normal as soon as the power goes back on. If someone accidentally turns a plug off, it'll turn itself back on.
* **Sunrise/Sunset:** No off the shelf solutions supports simulated sunrise and sunset via dimming, but this script does. This does require [dedicated hardware](https://www.amazon.com/smart-outdoor-dimmer-plug-kasa/dp/B09DT173R1), but I think it's worth the extra headache. That said, it's easy to remove this feature if you don't want it.

The main disadvantage of this script is that it needs to be running 24/7- meaning some kind of dedicated hardware is preferrable. It's lightweight enough that it should run on anything that supports Python, for instance, I'm running it on a Pi Zero. The other downside is that it is far and away the most complicated solution, requiring a fair amount of technical background to set up comfortably. That said, if you're comfortable with that, I think this solution will suit you better than any other.
