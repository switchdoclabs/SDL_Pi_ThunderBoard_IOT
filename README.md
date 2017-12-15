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

Testing The Setup<BR>

See the Testing setup in the SDL Tutorial on the Raspberry Pi IOT Thunder Board Kit: <BR>
http://www.switchdoc.com/2017/12/tutorial-building-an-iot-lightning-detector-with-your-raspberry-pi-part-1/



testThunderBoard.py - running this program detects the ThunderBoard at address 0x02 or 0x03 and starts detecting lightning <BR>

testLCD.py - running this program detects the LCD and displays a set of messages<BR>

ThunderBoardIOT.py - This is the software for the SwitchDoc Labs Raspberry Pi IOT Kit <BR>

Generating Lightning for the Thunder Board<BR>

Consider purchasing the SwitchDoc Labs Thunder Board Lightning Simulator at shop.switchdoc.com  <BR> 



