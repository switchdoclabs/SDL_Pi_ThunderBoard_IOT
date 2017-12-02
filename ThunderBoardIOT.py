#!/usr/bin/env python
#
# ThunderBoard IOT - SwitchDoc Labs
#
# November 2017
#

VERSIONNUMBER ="Pi003"
import sys
import os


import time

from pubnub.pubnub import PubNub
from pubnub.pubnub import PNConfiguration

# Check for user imports
try:
	import conflocal as config
except ImportError:
	import config


pnconf = PNConfiguration()
 
pnconf.subscribe_key = config.Pubnub_Subscribe_Key
pnconf.publish_key = config.Pubnub_Publish_Key
  
pubnub = PubNub(pnconf)

# lcd

import grove_lcd as lcd



import RPi.GPIO as GPIO


#set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


#Buzzer
BUZZER = 13
GPIO.setup(BUZZER, GPIO.OUT, initial=0)


LED = 4

GPIO.setup(LED, GPIO.OUT, initial=0)

from datetime import datetime

import pytz


from apscheduler.schedulers.background import BackgroundScheduler

import apscheduler.events
# lcd routines

def waitingForLightning():
	lcd.setRGB(0,255,0)
	lcd.setText("Waiting For\nLightning")

def displayNoise():
	lcd.setRGB(0,255,150)
	lcd.setText("Noise\nDetected")

def displayDisturber():
	lcd.setRGB(0,200,150)
	lcd.setText("Disturber\nDetected")


def startIOTLightning():
	lcd.setRGB(0,128,64)
  	lcd.setText("ThunderBoardIOT\nV"+VERSIONNUMBER);

def initializingIOT():
	lcd.setRGB(0,0,128)
  	lcd.setText("Initializing\nCalibration");

def ThunderBoardFound(address):
	lcd.setRGB(0,0,128)
  	lcd.setText("TBoard Found\nAddress="+address);

def displayLightning():
	lcd.setRGB(255,0,0)
  	lcd.setText("Lightning!! \nDistance="+str(LightningData.LastDistance)+"km");


# Buzzer

def buzzUser(count, spaceDelay):

	for i in range(0, count):
		GPIO.output(BUZZER, 1)
		time.sleep(spaceDelay)
		GPIO.output(BUZZER, 0)
		time.sleep(spaceDelay)

#setup Thunder Board Lightning Detector
from SDL_Pi_Thunderboard_AS3935 import  AS3935

import LightningData
# D16
InterruptGPIOpin = 16

startIOTLightning()

time.sleep(5)

sensor = AS3935(address=0x02, bus=1)

try:

       sensor.set_indoors(False)
       ThunderBoardFound("0x02")
       print "Thunder Board present at address 0x02"

except IOError as e:
        sensor = AS3935(address=0x03, bus=1)

        try:

                sensor.set_indoors(False)

       		ThunderBoardFound("0x03")
                print "Thunder Board present at address 0x03"

        except IOError as e:

                print "Thunder Board not present"
                exit()

time.sleep(3)

initializingIOT()

sensor.set_indoors(False)
sensor.set_noise_floor(0)

#if(sensor.runCalibration(InterruptGPIOpin) == False):
#    print("Tuning out of range, check your wiring, your sensor and make sure physics laws have not changed!");


sensor.calibrate(tun_cap=0x04)


sensor.set_min_strikes(1)


def readLightningStatus():

        noise_floor = sensor.get_noise_floor()
        min_strikes = sensor.get_min_strikes()
        indoor = sensor.get_indoors()
        mask_disturber = sensor.get_mask_disturber()
        disp_lco = sensor.get_disp_lco()
        #interrupt = sensor.get_interrupt()

	LightningData.Noise_Floor = noise_floor
 	LightningData.Minimum_Strikes = min_strikes
	LightningData.IndoorSet = indoor
	LightningData.Mask_Disturber = mask_disturber
	LightningData.Display_LCO = disp_lco
	
        print "---------"
        print "noise_floor=", noise_floor
        print "min_strikes=", min_strikes
        print "indoor=", indoor
        print "mask_disturber=", mask_disturber
        print "disp_lco=", disp_lco
        print "Interrupt Count=", LightningData.InterruptCount
        #print "interrupt=", interrupt




def handle_interrupt(channel):
    global count
    global sensor

    LightningData.InterruptCount = LightningData.InterruptCount + 1
    time.sleep(0.003)
    reason = sensor.get_interrupt()
    LightningData.LastInterruptResult = reason
    now = datetime.now().strftime('%H:%M:%S - %Y/%m/%d')
    tuple = time.tzname
    LightningData.InterruptTimeStamp = now + " " + tuple[0] 
    LightningData.InterruptTimeStamp
    print "Interrupt reason=", reason
    if reason == 0x01:
	LightningData.LastResult = "Noise level too high - adjusting"
	print LightningData.LastResult
        sensor.raise_noise_floor()
    elif reason == 0x04:
	LightningData.LastResult = "Disturber detected - masking"
        sensor.set_mask_disturber(True)
    elif reason == 0x08:
	LightningData.LightningCount = LightningData.LightningCount +1
	tuple = time.tzname
	LightningData.LightningTimeStamp = now + " " + tuple[0] 
        distance = sensor.get_distance()
	LightningData.LastDistance = distance
	LightningData.LastResult = "Lightning! " +str(distance) + "km away."
	LightningData.LastLightningResult = "Lightning! " +str(distance) + "km away."
	print LightningData.LastResult + LightningData.LightningTimeStamp
    
    LightningData.InterruptActive = True

GPIO.setup(InterruptGPIOpin, GPIO.IN, pull_up_down = GPIO.PUD_UP )
GPIO.add_event_detect(InterruptGPIOpin, GPIO.RISING, callback=handle_interrupt)

print "Waiting for lightning - or at least something that looks like it"




# setup apscheduler

def tick():
    print('Tick! The time is: %s' % datetime.now())


def killLogger():
    scheduler.shutdown()
    print "Scheduler Shutdown...."
    exit()

def blinkLED(times,length):

	for i in range(0, times):
		GPIO.output(LED, 1)
		time.sleep(length)
		GPIO.output(LED, 0)
		time.sleep(length)




def publish_callback(result, status):
        print "status.is_error", status.is_error()
        print "status.original_response", status.original_response
        pass
        # handle publish result, status always present, result if successful
        # status.isError to see if error happened



def publishLightningToPubNub():
	
        print('Publishing Data to PubNub time: %s' % datetime.now())
        print '		LastResult:             ' + str(LightningData.LastResult)

    	now = datetime.now().strftime('%H:%M:%S - %Y/%m/%d')
    	tuple = time.tzname
    	LightningData.LastPublishTimeStamp = now + " " + tuple[0]

        myMessage = { "SoftwareVersion": VERSIONNUMBER, "LastInterruptResult": LightningData.LastInterruptResult, "LastResult": LightningData.LastResult, "LastLightningResult": LightningData.LastLightningResult, "LightningTimeStamp": LightningData.LightningTimeStamp, "LightningCount": LightningData.LightningCount, "InterruptCount": LightningData.InterruptCount, "LastDistance":LightningData.LastDistance, "Noise_Floor": LightningData.Noise_Floor, "IndoorSet": LightningData.IndoorSet, "Display_LCO": LightningData.Display_LCO, "Minimum_Strikes": LightningData.Minimum_Strikes, "Mask_Disturber": LightningData.Mask_Disturber, "InterruptTimeStamp": LightningData.InterruptTimeStamp, "LastPublishTimeStamp": LightningData.LastPublishTimeStamp }
        pubnub.publish().channel('ThunderBoardIOT').message(myMessage).async(publish_callback)

        blinkLED(3,0.200)

	returnValue = []
	return returnValue

def ap_my_listener(event):
    if event.exception:
        print event.exception
        print event.traceback


print "-----------------"
print "ThunderBoard IOT"
print ""
print "SwitchDoc Labs" 
print "Version: ", VERSIONNUMBER
print "-----------------"
print ""


if __name__ == '__main__':



	# read initial state
	readLightningStatus()

	# publish initial state
	publishLightningToPubNub()

    	scheduler = BackgroundScheduler()
	
	#pubnub.subscribe(channels='my_channel', callback=callback, error=error, connect=connect, reconnect=reconnect, disconnect=disconnect)


	# DEBUG Mode - because the functions run in a separate thread, debugging can be difficult inside the functions.
	# we run the functions here to test them.
	#tick()

        scheduler.add_listener(ap_my_listener, apscheduler.events.EVENT_JOB_ERROR)    


	# prints out the date and time to console
    	scheduler.add_job(tick, 'interval', seconds=60)
    	# blink life light
	scheduler.add_job(blinkLED, 'interval', seconds=5, args=[1,0.250])

	# add the Update to PubNub 
	scheduler.add_job(publishLightningToPubNub, 'interval', seconds=120)

	# check configuration
	scheduler.add_job(readLightningStatus, 'interval', seconds=3600)


    	# start scheduler
	scheduler.start()
	print "-----------------"
	print "Scheduled Jobs" 
	print "-----------------"
    	scheduler.print_jobs()
	print "-----------------"
	waitingForLightning()

    	print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    	try:
        	# This is here to simulate application activity (which keeps the main thread alive).
                while True:
            		time.sleep(1)


			# display lightning on LCD
			if (LightningData.InterruptActive == True):
				if (LightningData.LastInterruptResult == 0x08):
		
							
					displayLightning()
						
					# beep user

					if (LightningData.LastDistance <=1):
						buzzUser(3, 0.2)
					elif (LightningData.LastDistance < 15):
						buzzUser(2, 0.2)
					else:
						buzzUser(1, 0.2)
						


					publishLightningToPubNub()
					LightningData.InterruptActive = False
					time.sleep(1)

				elif (LightningData.LastInterruptResult == 0x04):

					print "Disturber Found"
					displayDisturber()
					publishLightningToPubNub()
					LightningData.InterruptActive = False
					time.sleep(1)

				elif (LightningData.LastInterruptResult == 0x01):

					print "Noise Found "
					displayNoise()
					publishLightningToPubNub()
					LightningData.InterruptActive = False
					time.sleep(1)

				waitingForLightning()

    	except (KeyboardInterrupt, SystemExit):
        	# Not strictly necessary if daemonic mode is enabled but should be done if possible
        	scheduler.shutdown
