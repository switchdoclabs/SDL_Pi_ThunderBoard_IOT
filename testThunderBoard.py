#!/usr/bin/env python
from SDL_Pi_Thunderboard_AS3935 import  AS3935

import RPi.GPIO as GPIO
import time
from datetime import datetime

GPIO.setmode(GPIO.BCM)

InterruptGPIOpin = 16


sensor = AS3935(address=0x02, bus=1)


try:

       sensor.set_indoors(False)
                
       print "Thunder Board present at address 0x02"

except IOError as e:
	sensor = AS3935(address=0x03, bus=1)

        try:

               	sensor.set_indoors(False)
                
               	print "Thunder Board present at address 0x03"

       	except IOError as e:

        	print "Thunder Board not present"
		exit()

sensor.set_indoors(False)
sensor.set_noise_floor(0)
sensor.calibrate(tun_cap=0x09)
sensor.set_min_strikes(1)

count = 0
runcount = 0
def handle_interrupt(channel):
    global count
    count = count + 1
    time.sleep(0.003)
    global sensor
    reason = sensor.get_interrupt()
    print "Interrupt reason=", reason
    if reason == 0x01:
        print "Noise level too high - adjusting"
        sensor.raise_noise_floor()
    elif reason == 0x04:
        print "Disturber detected - masking"
        sensor.set_mask_disturber(True)
    elif reason == 0x08:
        now = datetime.now().strftime('%H:%M:%S - %Y/%m/%d')
        distance = sensor.get_distance()
        print "We sensed lightning!"
        print "It was " + str(distance) + "km away. (%s)" % now
        print ""


#GPIO.setup(InterruptGPIOpin, GPIO.IN )
GPIO.setup(InterruptGPIOpin, GPIO.IN, pull_up_down = GPIO.PUD_UP )
GPIO.add_event_detect(InterruptGPIOpin, GPIO.RISING, callback=handle_interrupt)

print "Waiting for lightning - or at least something that looks like it"


def readLightningStatus():

	distance = sensor.get_distance()
	noise_floor = sensor.get_noise_floor()
	min_strikes = sensor.get_min_strikes()
	indoor = sensor.get_indoors()
	mask_disturber = sensor.get_mask_disturber()
	disp_lco = sensor.get_disp_lco()
	#interrupt = sensor.get_interrupt()

	print "---------"
	print "distance=", distance
	print "noise_floor=", noise_floor
	print "min_strikes=", min_strikes
	print "indoor=", indoor
	print "mask_disturber=", mask_disturber
	print "disp_lco=", disp_lco
	print "count=", count
	#print "interrupt=", interrupt
	

while True:
    time.sleep(1.0)
    #readLightningStatus()
