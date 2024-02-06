# Precision Irrigation script that follows irrigation timer schedule
import RPi.GPIO as GPIO
import time
from os.path import exists
from datetime import datetime
import pandas as pd

# Check if data CSV exists, create it if not
file_exists = exists("/home/picam/Desktop/irrigation_data.csv")

if file_exists == True:
    print("Data file exists, proceeding with irrigation check.")
    pre_dat = pd.read_csv(r'/home/picam/Desktop/irrigation_data.csv')
elif file_exists == False:
    print("Data file does not exist, creating data file.")
    pre_dat = pd.DataFrame(columns = ['Date', 'Treatment', 'Time', 'Pulses', 'Volume'])

# Set high and low irrigation flow meter data pins
flow_hi_GPIO = 11 #FLOW_SENSOR_GPIO = 11
flow_lo_GPIO = 26

# Set high and low flow rates
flow_rate_hi = 1800 # pulses per gallon
flow_rate_lo = 900 # pulses per gallon

# Set high and low flow time in seconds
lo_water_sec = 1200 # 1200 for 20 minutes
hi_water_sec = 2400 # 2400 for 40 minutes

# Set flow volume
low_vol_av = 60
low_vol_cn = 50
hi_vol_av = 120
hi_vol_cn = 100

# Set up the GPIO board
GPIO.setmode(GPIO.BCM)

# Setup pulse counter for flow meter
GPIO.setup(flow_hi_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(flow_lo_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
 
global count
count = 0
 
def countPulse(channel):
   global count
   if start_counter == 1:
      count = count+1
 
GPIO.add_event_detect(flow_hi_GPIO, GPIO.FALLING, callback=countPulse)
GPIO.add_event_detect(flow_lo_GPIO, GPIO.FALLING, callback=countPulse)

# Define which GPIO pins are connected to relays
pinList = [2, 3, 4, 17, 27, 22, 10, 9]

# loop through pins and set mode and state to 'low'
for i in pinList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)
    
# Turn on CN Low for specified time
print ("Irrigation: CONTROL LOW ON")
GPIO.output(2, GPIO.LOW) # 1
start_time = time.time()

# Take image timestamp
now = datetime.now()
irr_date = now.strftime('%Y_%m_%d_%H_%M_%S')
print("Timestamp:", irr_date)

# Start flow meter
start_counter = 1

while True:
    time.sleep(1)
    
    current_time = time.time()
    elapsed_time = current_time - start_time
    
    if elapsed_time > 1500:
        start_counter = 0
        print("Total irrigation time: " + str(int(elapsed_time))  + " seconds")
        print("Total Pulses: " + str(int(count)))
        flow = (count / flow_rate_lo)
        print("Total irrigation volume is: %.3f Gallons" % (flow))
        
        # Append to numpy array
        pre_dat = pre_dat.append({'Date' : irr_date, 'Treatment' : 'Control Low', 'Time' : elapsed_time, 'Pulses' : count, 'Volume' : flow}, ignore_index = True)
        print(pre_dat)
        
        count = 0
        break
    elif (count / flow_rate_lo) >= low_vol_cn:
        start_counter = 0
        print("Total irrigation time: " + str(int(elapsed_time))  + " seconds")
        print("Total Pulses: " + str(int(count)))
        flow = (count / flow_rate_lo)
        print("Total irrigation volume is: %.3f Gallons" % (flow))
        
        # Append to numpy array
        pre_dat = pre_dat.append({'Date' : irr_date, 'Treatment' : 'Control Low', 'Time' : elapsed_time, 'Pulses' : count, 'Volume' : flow}, ignore_index = True)
        print(pre_dat)
        
        count = 0
        break

# Turn off CN low irrigation
print ("Irrigation: CONTROL LOW OFF")
GPIO.output(2, GPIO.HIGH) #1

# Turn on AV Low for specified time
print ("Irrigation: AGRIVOLTAIC LOW ON")
GPIO.output(27, GPIO.LOW) # 5
start_time = time.time()

# Take image timestamp
now = datetime.now()
irr_date = now.strftime('%Y_%m_%d_%H_%M_%S')
print("Timestamp:", irr_date)

# Start flow meter
start_counter = 1

while True:
    time.sleep(1)
    
    current_time = time.time()
    elapsed_time = current_time - start_time
    
    if elapsed_time > 1500:
        start_counter = 0
        print("Total irrigation time: " + str(int(elapsed_time))  + " seconds")
        print("Total Pulses: " + str(int(count)))
        flow = (count / flow_rate_lo)
        print("Total irrigation volume is: %.3f Gallons" % (flow))
        
        # Append to numpy array
        pre_dat = pre_dat.append({'Date' : irr_date, 'Treatment' : 'Agrivoltaic Low', 'Time' : elapsed_time, 'Pulses' : count, 'Volume' : flow}, ignore_index = True)
        print(pre_dat)
        
        count = 0
        break
    elif (count / flow_rate_lo) >= low_vol_av:
        start_counter = 0
        print("Total irrigation time: " + str(int(elapsed_time))  + " seconds")
        print("Total Pulses: " + str(int(count)))
        flow = (count / flow_rate_lo)
        print("Total irrigation volume is: %.3f Gallons" % (flow))
        
        # Append to numpy array
        pre_dat = pre_dat.append({'Date' : irr_date, 'Treatment' : 'Agrivoltaic Low', 'Time' : elapsed_time, 'Pulses' : count, 'Volume' : flow}, ignore_index = True)
        print(pre_dat)
        
        count = 0
        break

print ("Irrigation: AGRIVOLTAIC LOW OFF")
GPIO.output(27, GPIO.HIGH) #5

# Turn on control low irrigation for specified time
print ("Irrigation: CONTROL HIGH ON")
GPIO.output(3, GPIO.LOW) #2
start_time = time.time()

# Take image timestamp
now = datetime.now()
irr_date = now.strftime('%Y_%m_%d_%H_%M_%S')
print("Timestamp:", irr_date)

# Start flow meter
start_counter = 1

while True:
    time.sleep(1)
    
    current_time = time.time()
    elapsed_time = current_time - start_time
    
    if elapsed_time > 2700:
        start_counter = 0
        print("Total irrigation time: " + str(int(elapsed_time))  + " seconds")
        print("Total Pulses: " + str(int(count)))
        flow = (count / flow_rate_hi)
        print("Total irrigation volume is: %.3f Gallons" % (flow))
        
        # Append to numpy array
        pre_dat = pre_dat.append({'Date' : irr_date, 'Treatment' : 'Control High', 'Time' : elapsed_time, 'Pulses' : count, 'Volume' : flow}, ignore_index = True)
        print(pre_dat)
        
        count = 0
        break
    elif (count / flow_rate_hi) >= hi_vol_cn:
        start_counter = 0
        print("Total irrigation time: " + str(int(elapsed_time))  + " seconds")
        print("Total Pulses: " + str(int(count)))
        flow = (count / flow_rate_hi)
        print("Total irrigation volume is: %.3f Gallons" % (flow))
        
        # Append to numpy array
        pre_dat = pre_dat.append({'Date' : irr_date, 'Treatment' : 'Control High', 'Time' : elapsed_time, 'Pulses' : count, 'Volume' : flow}, ignore_index = True)
        print(pre_dat)
        
        count = 0
        break

# Turn control high irrigation off
print ("Irrigation: CONTROL HIGH OFF")
GPIO.output(3, GPIO.HIGH) #2

# Turn on agrivoltaic high for specified time
print ("Irrigation: AGRIVOLTAIC HIGH ON")
GPIO.output(4, GPIO.LOW) #3
start_time = time.time()

# Take image timestamp
now = datetime.now()
irr_date = now.strftime('%Y_%m_%d_%H_%M_%S')
print("Timestamp:", irr_date)

# Start flow meter
start_counter = 1

while True:
    time.sleep(1)
    
    current_time = time.time()
    elapsed_time = current_time - start_time
    
    if elapsed_time > 2700:
        start_counter = 0
        print("Total irrigation time: " + str(int(elapsed_time))  + " seconds")
        print("Total Pulses: " + str(int(count)))
        flow = (count / flow_rate_hi)
        print("Total irrigation volume is: %.3f Gallons" % (flow))
        
        # Append to numpy array
        pre_dat = pre_dat.append({'Date' : irr_date, 'Treatment' : 'Agrivoltaic High', 'Time' : elapsed_time, 'Pulses' : count, 'Volume' : flow}, ignore_index = True)
        print(pre_dat)
        
        count = 0
        break
    elif (count / flow_rate_hi) >= hi_vol_av:
        start_counter = 0
        print("Total irrigation time: " + str(int(elapsed_time))  + " seconds")
        print("Total Pulses: " + str(int(count)))
        flow = (count / flow_rate_hi)
        print("Total irrigation volume is: %.3f Gallons" % (flow))
        
        # Append to numpy array
        pre_dat = pre_dat.append({'Date' : irr_date, 'Treatment' : 'Agrivoltaic High', 'Time' : elapsed_time, 'Pulses' : count, 'Volume' : flow}, ignore_index = True)
        print(pre_dat)
        
        count = 0
        break

#time.sleep(60) # 60 seconds times 40 minutes = 2400
print ("Irrigation: AGRIVOLtAIC HIGH OFF")
GPIO.output(4, GPIO.HIGH) #3

# Reset GPIO settings
GPIO.cleanup()

# Save as CSV
pre_dat.to_csv("/home/picam/Desktop/irrigation_data.csv", index=False)
