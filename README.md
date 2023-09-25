# What this is
A simple script that automatically syncs a Kasa smart strip and some dimmer bulbs to a day/night cycle anywhere in the world. I keep reptiles, so I use this to simulate a more natural environment in their enclosures than what off-the-shelf solutions provide. I designed the script to be ran on a dedicated server such as a Pi Zero W, but you can run it anywhere as long as it's on the same network as your hardware.

# Setup
**Requires** Python 3.10, a Kasa Smart Strip, and at least one Kasa Smart Dimmer
1. Install requirements.txt
2. [Follow the guide here to get your Kasa device information](https://python-kasa.readthedocs.io/en/latest/)
3. Modify the config section so that it accurately reflects your setup and needs
4. Run the script

# Existing solutions
There are four solutions that currently exist for managing reptile lights.
1. ### Manual

   There are some pretty obvious problems with manually turning your reptile lights on or off that boil down to excess labor and human error. This isn't an ideal solution, but there are some advantages. It's free, and in theory you could perfectly simulate whatever day/night cycle you want.
2. ### Mechanical timers

   [Timers like these](https://www.amazon.com/GE-Mechanical-Intervals-Decorations-46211/dp/B07YQKNC4D/ref=sr_1_5?keywords=mechanical+outlet+timer&qid=1695593724&sr=8-5) are cheap, intuitive, and widely available, making them a popular entry-level timer. However, they come with two serious downsides- they often tend to be noisy, and they all drift. You'll have to stay on top of updating your timer if you want to simulate seasonal changes in daylight, and, you'll have to remmeber to update it if there's an outage.
3. ### Electrical timers

   [Electrical timers](https://www.amazon.com/Fosmon-Programmable-Seasonal-Portable-Aquarium/dp/B07HCQKRRY/ref=sr_1_6?keywords=outlet%2Btimer&qid=1695594132&sr=8-6&th=1) are very similar to mechanical timers, but use electrical circuitry rather than mechanics to calculate time of day. Nowadays, they're barely more expensive than mechanical timers, and remove the noise problem entirely. They're also less prone to drift than mechanical timers, though, it will still happen over time. Otherwise, they function identically and carry the same downsides to mechanical timers. In my opinion they're strictly superior to mechanical timers, barring that some may have a slightly less intuitive user interface.
4. ### Smart plugs

   [Smart plugs](https://www.amazon.com/BN-LINK-Monitoring-Function-Compatible-Assistant/dp/B07CVPKD8Z/ref=sxin_14_pa_sp_search_thematic_sspa?content-id=amzn1.sym.1c86ab1a-a73c-4131-85f1-15bd92ae152d%3Aamzn1.sym.1c86ab1a-a73c-4131-85f1-15bd92ae152d&cv_ct_cx=outlet+timer&keywords=outlet+timer&pd_rd_i=B07CVPKD8Z&pd_rd_r=e67b4845-b45c-4157-b841-5e58270cb774&pd_rd_w=UkVWU&pd_rd_wg=v4H3c&pf_rd_p=1c86ab1a-a73c-4131-85f1-15bd92ae152d&pf_rd_r=YZVE1NQHJJXHBENVCX92&qid=1695594132&sbo=RZvfv%2F%2FHxDF%2BO5021pAnSA%3D%3D&sr=1-2-364cf978-ce2a-480a-9bb0-bdb96faa0f61-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9zZWFyY2hfdGhlbWF0aWM&psc=1) provide a pretty interesting alternative solution. Because they're internet-enabled, they're completely immune to drift & resilient to power outages and, because they're fully electric, they're completely silent too. Many also come standard with programmable features such as turning on and off at sunrise/sunset, and are often dirt cheap. In many ways, these are an ideal solution for your average reptile keeper. There are a few downsides, though- chiefly that you're at the mercy of the manufacturer. Some can be controlled by an app, some require a hub; some apps are good, some apps suck; some apps require your phone to be on the same network which can be a real headache when you're traveling. There's also all the usual security and privacy risks that you get when you're using devices like these. Finally, they do tend to be a bit setup-heavy compared to mechanical/electric timers, requiring you to install an app, connect the devices to your network, and configure the devices.

## My solution
I've used all of these solutions with my reptiles at various points, and I definitely favor smart plugs. However, the bad apps and travel issues kept me from being truly happy with that solution, so I decided to devise my own, which lead me to building this script. It uses Kasa brand smart devices, because, at time of writing, they have a great API and Python library that makes interacting with them super easy. As I continued development, I found a few more advantages to my solution as well.
* **No app:** No app means no reliance on any infrastructure other than my own. In today's world where any service can be killed at any moment, this provides me with a huge amount of peace of mind.
* **Robust:** If the power goes out, I can trust that everything will go back to normal as soon as the power goes back on. If someone accidentally turns a plug off, it'll turn itself back on.
* **Sunrise/Sunset:** None of the off the self solutions support a simulated sunrise and sunset via dimming, but this script does. This is an optional feature as it requires [dedicated hardware](https://www.amazon.com/smart-outdoor-dimmer-plug-kasa/dp/B09DT173R1), but I really like it.

The main disadvantage of this script is that it needs to be running 24/7, or close to it, for best results- meaning some kind of dedicated hardware solution is needed. I decided to run it on a Pi Zero W, which has worked very well for me- it should run just fine on anything that has a WiFi connection and can install Python 3.
