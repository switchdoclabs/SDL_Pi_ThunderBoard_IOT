
import time
import grove_lcd as lcd

print "Testing LCD ------"


lcd.setText("Hello world\nThis is an LCD test")
lcd.setRGB(0,128,64)
time.sleep(2)
for c in range(255,0,-1):
     lcd.setText_norefresh("Going to sleep in {}...".format(str(c)))
     lcd.setRGB(c,255-c,0)
     time.sleep(0.1)
lcd.setRGB(0,255,0)
lcd.setText("Bye bye, this should wrap onto next line")

print "Testing LCD Complete ------"

