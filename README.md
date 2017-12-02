SwitchDoc Labs November, 2017<BR>

ThunderBoard IOT Code by SwitchDoc Labs  

Version Pi003 December 2, 2017 - Initial Release

To install:

Make sure you installed I2C as in this link:

https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c

Installing apscheduler

sudo apt-get install python-pip<BR>
sudo pip install setuptools --upgrade<BR>
sudo pip install apscheduler<BR>

Installing PubNub<BR>

sudo pip install pubnub<BR>

Testing The Thunder Board <BR>

Interrupt Grove Connector connected to D16 GPIO<BR>
I2C Grove Connector connected to I2C<BR>

testThunderBoard.py - running this program detects the ThunderBoard at address 0x02 or 0x03 and starts detecting lightning <BR>

ThunderBoardIOT.py - This is the software for the SwitchDoc Labs Raspberry Pi IOT Kit <BR>

Generating Lightning for the Thunder Board<BR>

Consider purchasing the SwitchDoc Labs Thunder Board Lightning Simulator at shop.switchdoc.com  <BR> 



