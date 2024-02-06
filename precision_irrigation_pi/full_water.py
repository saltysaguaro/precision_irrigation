# -------------------------------------------------------------------- #
# The following script controls irrigation for the experimental        #
# agrivoltaic plots at the Biosphere 2 research site. The script       #
# imports soil moisture data from a dense array of Campbell Scientific #
# sensors installed in the agrivoltaic and control gardens to support  #
# responsive precision irrigation. Built for RPi 3B.                   #
# -------------------------------------------------------------------- #

# Set precision irrigation thresholds and irrigation volume
irr_time = 60 # number of minutes to run irrigation for all beds

water_avhi = False
water_avlo = False
water_cnhi = True
water_cnlo = False

# Import libraries
import RPi.GPIO as GPIO
import time

# -------------------------------------------------------------------- #
#              Initiate the GPIO Board for relay control               #
# -------------------------------------------------------------------- #

# Set up the GPIO board
GPIO.setmode(GPIO.BCM)

# Define which GPIO pins are connected to relays
pinList = [2, 3, 4, 17, 27, 22, 10, 9]

# loop through pins and set mode and state to 'low'
for i in pinList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)

# -------------------------------------------------------------------- #
#             Turn on water for all beds for specified time            #
# -------------------------------------------------------------------- #

# Turn all irrigation valves on!
print("Turning selected irrigation valves on!")
if water_avlo == True:
    GPIO.output(27, GPIO.LOW) # 5
    print("AVLO: ON")
if water_avhi == True:
    GPIO.output(4, GPIO.LOW) # 3
    print("AVHI: ON")
if water_cnhi == True:
    GPIO.output(2, GPIO.LOW) # 1
    print("CNHI: ON")
if water_cnlo == True:
    GPIO.output(3, GPIO.LOW) # 2
    print("CNLO: ON")
start_time = time.time()

while True:
    time.sleep(1)
    
    current_time = time.time()
    elapsed_time = current_time - start_time
    
    if elapsed_time > (irr_time*60):
        print('Irrigation time reached; stopping irrigation after ' + str(elapsed_time/60))
        break

print ("Turning all irrigation valves off!")
GPIO.output(27, GPIO.HIGH) # 5
GPIO.output(4, GPIO.HIGH) # 3
GPIO.output(2, GPIO.HIGH) # 1
GPIO.output(3, GPIO.HIGH) # 2

# Reset GPIO settings
GPIO.cleanup()
