import time
import RPi.GPIO as GPIO

class AS3935:
    """A basic class used for interacting with the AS3935 lightning
    sensor from a Raspberry Pi over I2C"""

    def __init__(self, address, bus=0):
        self.address = address
        import smbus
        self.i2cbus = smbus.SMBus(bus)

    def calibrate(self, tun_cap=None):
        """Calibrate the lightning sensor - this takes up to half a second
        and is blocking.

        The value of tun_cap should be between 0 and 15, and is used to set
        the internal tuning capacitors (0-120pF in steps of 8pF)
        """
        time.sleep(0.08)
        self.read_data()
        if tun_cap is not None:
            if tun_cap < 0x10 and tun_cap > -1:
                self.set_byte(0x08, (self.registers[0x08] & 0xF0) | tun_cap)
                time.sleep(0.002)
            else:
                raise Exception("Value of TUN_CAP must be between 0 and 15")
        self.set_byte(0x3D, 0x96)
        time.sleep(0.002)
        self.set_byte(0x08, self.registers[0x08] | 0x20)
        time.sleep(0.002)
        self.read_data()
        self.set_byte(0x08, self.registers[0x08] & 0xDF)
        time.sleep(0.002)

    '''
    def runCalibration(self,InterruptGPIOpin):
	GPIO.setup(InterruptGPIOpin, GPIO.IN, pull_up_down = GPIO.PUD_UP )
	target = 3125
	currentcount = 0
	bestdiff = 16000
	currdiff = 0
	bestTune = 0
	currTune = 0
	# set lco_fdiv divider to 0, which translates to 16
	# so we are looking for 31250Hz on irq pin
	# and since we are counting for 100ms that translates to number 3125
	# each capacitor changes second least significant digit
	# using this timing so this is probably the best way to go
	self.write_register(0x03, 0)	
	#registerWrite(AS3935_LCO_FDIV,0);
	self.write_register(0x08, 1)	
	#registerWrite(AS3935_DISP_LCO,1);
	# tuning is not linear, can't do any shortcuts here
	# going over all built-in cap values and finding the best
	#for (currTune = 0; currTune <= 0x0F; currTune++) 
	for currTune in range (0, 0x0f):

		self.write_register(0x08, currTune)	
		#registerWrite(AS3935_TUN_CAP,currTune);
		# let it settle
		time.sleep(0.002);
		currentcount = 0;
		prevIrq = GPIO.input(InterruptGPIOpin);
		setUpTime = self.Tmillis() + 100;
		while((self.Tmillis() - setUpTime) < 0):

			currIrq = GPIO.input(InterruptGPIOpin);
			if (currIrq > prevIrq):
				currentcount= currentcount+1	
			prevIrq = currIrq

		currdiff = target - currentcount
		# don't look at me, abs() misbehaves
		if(currdiff < 0):
			currdiff = -currdiff;
		if(bestdiff > currdiff):
		
			bestdiff = currdiff;
			bestTune = currTune;
	

	self.write_register(0x08, bestTune)	
	#registerWrite(AS3935_TUN_CAP,bestTune);
	time.sleep(0.002);
	self.write_register(0x08, 0)	
	#registerWrite(AS3935_DISP_LCO,0);
	# and now do RCO calibration
    	I2c.write((uint8_t)_ADDR, (uint8_t)0x3D, (uint8_t)0x96);
        
	time.sleep(0.003);
	# if error is over 109, we are outside allowed tuning range of +/-3.5%
    	print "bestTune = ", bestTune
    	print "Difference =", bestdiff
	if (bestdiff > 109): 
		return False
	else:
		return True

	#return bestdiff > 109?false:true;
    '''
    def reset(self):
        """Reset all registers to their default power on values
        """
        self.set_byte(0x3C, 0x96)

    def get_interrupt(self):
        """Get the value of the interrupt register

        0x01 - Too much noise
        0x04 - Disturber
        0x08 - Lightning
        """
        self.read_data()
        return self.registers[0x03] & 0x0F

    def get_distance(self):
        """Get the estimated distance of the most recent lightning event
        """
        self.read_data()
        if self.registers[0x07] & 0x3F == 0x3F:
            return False
        else:
            return self.registers[0x07] & 0x3F

    def get_noise_floor(self):
        """Get the noise floor value.

        Actual voltage levels used in the sensor are located in Table 16
        of the data sheet.
        """
        self.read_data()
        return (self.registers[0x01] & 0x70) >> 4

    def set_noise_floor(self, noisefloor):
        """Set the noise floor value.

        Actual voltage levels used in the sensor are located in Table 16
        of the data sheet.
        """
        self.read_data()
        noisefloor = (noisefloor & 0x07) << 4
        write_data = (self.registers[0x01] & 0x8F) + noisefloor
        self.set_byte(0x01, write_data)

    def lower_noise_floor(self, min_noise=0):
        """Lower the noise floor by one step.

        min_noise is the minimum step that the noise_floor should be
        lowered to.
        """
        floor = self.get_noise_floor()
        if floor > min_noise:
            floor = floor - 1
            self.set_noise_floor(floor)
        return floor

    def raise_noise_floor(self, max_noise=7):
        """Raise the noise floor by one step

        max_noise is the maximum step that the noise_floor should be
        raised to.
        """
        floor = self.get_noise_floor()
        if floor < max_noise:
            floor = floor + 1
            self.set_noise_floor(floor)
        return floor

    def get_min_strikes(self):
        """Get the number of lightning detections required before an
        interrupt is raised.
        """
        self.read_data()
        value = (self.registers[0x02] >> 4) & 0x03
        if value == 0:
            return 1
        elif value == 1:
            return 5
        elif value == 2:
            return 9
        elif value == 3:
            return 16

    def set_min_strikes(self, minstrikes):
        """Set the number of lightning detections required before an
        interrupt is raised.

        Valid values are 1, 5, 9, and 16, any other raises an exception.
        """
        if minstrikes == 1:
            minstrikes = 0
        elif minstrikes == 5:
            minstrikes = 1
        elif minstrikes == 9:
            minstrikes = 2
        elif minstrikes == 16:
            minstrikes = 3
        else:
            raise Exception("Value must be 1, 5, 9, or 16")

        self.read_data()
        minstrikes = (minstrikes & 0x03) << 4
        write_data = (self.registers[0x02] & 0xCF) + minstrikes
        self.set_byte(0x02, write_data)

    def get_indoors(self):
        """Determine whether or not the sensor is configured for indoor
        use or not.

        Returns True if configured to be indoors, otherwise False.
        """
        self.read_data()
        if self.registers[0x00] & 0x10 == 0x10:
            return True
        else:
            return False

    def set_indoors(self, indoors):
        """Set whether or not the sensor should use an indoor configuration.
        """
        self.read_data()
        if indoors:
            write_value = (self.registers[0x00] & 0xE0) + 0x12
        else:
            write_value = (self.registers[0x00] & 0xE0) + 0x0E
        self.set_byte(0x00, write_value)

    def set_mask_disturber(self, mask_dist):
        """Set whether or not disturbers should be masked (no interrupts for
        what the sensor determines are man-made events)
        """
        self.read_data()
        if mask_dist:
            write_value = self.registers[0x03] | 0x20
        else:
            write_value = self.registers[0x03] & 0xDF
        self.set_byte(0x03, write_value)

    def get_mask_disturber(self):
        """Get whether or not disturbers are masked or not.

        Returns True if interrupts are masked, false otherwise
        """
        self.read_data()
        if self.registers[0x03] & 0x20 == 0x20:
            return True
        else:
            return False

    def set_disp_lco(self, display_lco):
        """Have the internal LC oscillator signal displayed on the interrupt pin for
        measurement.

        Passing display_lco=True enables the output, False disables it.
        """
        self.read_data()
        if display_lco:
            self.set_byte(0x08, (self.registers[0x08] | 0x80))
        else:
            self.set_byte(0x08, (self.registers[0x08] & 0x7F))
        time.sleep(0.002)

    def get_disp_lco(self):
        """Determine whether or not the internal LC oscillator is displayed on the
        interrupt pin.

        Returns True if the LC oscillator is being displayed on the interrupt pin,
        False otherwise
        """
        self.read_data()
        if self.registers[0x08] & 0x80 == 0x80:
            return True
        else:
            return False
    
    def Tmillis(self):
    		return int(round(time.time() * 1000))

    def set_byte(self, register, value):
        """Write a byte to a particular address on the sensor.

        This method should rarely be used directly.
        """

        self.i2cbus.write_byte_data(self.address, register, value)

    '''

    def _ffsz(self, mask):
	
		i = 0;
		if (mask):
			for i in range (1, ~mask &1 ):
				mask >>= 1;
		return i;



    def write_register(self, register, mask, value):
        """Write a masked byte to a particular address on the sensor.

        This method should rarely be used directly.
        """

	print "regW ",register
  	print mask
  	print " " 
  	print value
  	print " read " 


  	#do masking
	regval &= ~(mask);
	if (mask):
		regval |= (data << (_ffsz(mask)-1));
	else:
		regval |= data;
    	print(" write ");
    	print(regval,HEX);
    	print(" err ");


        self.i2cbus.write_byte_data(self.address, register, value)
    '''


    def read_data(self):
        """
        Read a block of data from the sensor and store it.

        This doesn't read exact registers because the library used by
        smbus doesn't support repeated I2C starts (required to read
        registers directly on the sensor)

        This method should rarely be called directly.
        """
        self.registers = self.i2cbus.read_i2c_block_data(self.address, 0x00)
