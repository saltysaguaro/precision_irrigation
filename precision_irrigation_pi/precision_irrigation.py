# -------------------------------------------------------------------- #
# The following script controls irrigation for the experimental        #
# agrivoltaic plots at the Biosphere 2 research site. The script       #
# imports soil moisture data from a dense array of Campbell Scientific #
# sensors installed in the agrivoltaic and control gardens to support  #
# responsive precision irrigation. Built for RPi 3B.                   #
# -------------------------------------------------------------------- #

# Set precision irrigation thresholds and irrigation volume
thresh_hi = 0.25 # volumetric soil moisture (g^3/g^3)
thresh_lo = 0.15 # volumetric soil moisture (g^3/g^3)
irr_vol = 60 # irrigation volume in gallons

# Set high and low flow rates
flow_rate_hi = 1800 # pulses per gallon
flow_rate_lo = 900 # pulses per gallon

# Set high and low irrigation flow meter data pins
flow_hi_GPIO = 11
flow_lo_GPIO = 26

# Import libraries
import RPi.GPIO as GPIO
import time
import os
from datetime import datetime, timedelta
import pandas as pd
import re
import numpy as np

# -------------------------------------------------------------------- #
#                       Define Global Variables                        #
# -------------------------------------------------------------------- #

global count
global start_counter
global elapsed_time
global flow

count = 0
start_counter = 0
 
def countPulse(channel):
   global count
   global start_counter

   if start_counter == 1:
      count = count+1

# -------------------------------------------------------------------- #
#              Initiate the GPIO Board for relay control               #
# -------------------------------------------------------------------- #

# Set up the GPIO board
GPIO.setmode(GPIO.BCM)

# Setup pulse counter for flow meter
GPIO.setup(flow_hi_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(flow_lo_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
 
GPIO.add_event_detect(flow_hi_GPIO, GPIO.FALLING, callback=countPulse)
GPIO.add_event_detect(flow_lo_GPIO, GPIO.FALLING, callback=countPulse)

# Define which GPIO pins are connected to relays
pinList = [2, 3, 4, 17, 27, 22, 10, 9]

# loop through pins and set mode and state to 'low'
for i in pinList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)

# -------------------------------------------------------------------- #
#           Import, format, and extract soil moisture data             #
# -------------------------------------------------------------------- #

# Open our data file, and create it if it doesn't exist; then, add a header if the file is empty, and close the file
datafile = open('/home/picam/Desktop/data_irrigation.txt', 'a')
if os.stat('/home/picam/Desktop/data_irrigation.txt').st_size == 0:
    datafile.write('Date,Treatment,AVLO,AVHI,CNLO,CNHI,Time,Pulses,Volume,Comment\n')
datafile.close()

# Define a function for writing to the data file
def irrData(treatment, avlo, avhi, cnlo, cnhi, irrtime, irrpulse, irrvol, irrcomm):

    # Open data file in append mode ("a")
    datafile = open('/home/picam/Desktop/data_irrigation.txt', 'a')

    # Grab the current time
    now = datetime.now()
    cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
    datafile.write(str(cur_time) + ',' + treatment + ',' + str(avlo) + ',' + str(avhi) + ',' + str(cnlo) + ',' + str(cnhi) + ',' + str(irrtime) + ',' + str(irrpulse) + ',' + str(irrvol) + ',' + irrcomm + '\n')
    datafile.close()

# Create a backup irrigation function that delivers the specified volume of water
def specIrr(specvol, specpin, specflow, specmin, spectreat):

    global count
    global start_counter
    global elapsed_time
    global flow

    # Start flow meter
    start_counter = 1

    # Log the irrigation
    print(spectreat + ' sensor data is stale and hit a daily increment; watering on backup!')

    GPIO.output(specpin, GPIO.LOW) # 5
    start_time = time.time()

    # Log irrigation start
    irrData('none', 0, 0, 0, 0, 0, 0, 0, spectreat + ' water turned on!')

    while True:
        time.sleep(1)
        
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        if elapsed_time > (specmin*60):
            start_counter = 0
            print("Total irrigation time: " + str(int(elapsed_time))  + " seconds")
            print("Total Pulses: " + str(int(count)))
            flow = (count / specflow)
            print("Total irrigation volume is: %.3f Gallons" % (flow))
            
            # Append to numpy array
            irrData(spectreat, 0, 0, 0, 0, elapsed_time, count, flow, 'Backup watering reached safety shutoff: ' + str(specmin) + ' minutes')
            
            count = 0
            break
        elif (count / specflow) >= specvol:
            start_counter = 0
            print("Total irrigation time: " + str(int(elapsed_time))  + " seconds")
            print("Total Pulses: " + str(int(count)))
            flow = (count / specflow)
            print("Total irrigation volume is: %.3f Gallons" % (flow))
            
            # Append to numpy array
            irrData(spectreat, 0, 0, 0, 0, elapsed_time, count, flow, str(specvol) + ' gallons delivered successfully')
            
            count = 0
            break

    print ("Irrigation: AGRIVOLTAIC LOW OFF")
    GPIO.output(specpin, GPIO.HIGH) #5

# Import Campbell Scientific soil moisture sensor files
print("Importing Agrivoltaic Sensor Data")
sensor_av = pd.read_csv(r"https://agrivoltaicatlas.com/data_ref/irrigationB2pv.txt")
print(sensor_av)

# Log that agrivoltaic data is improted
irrData('none', 0, 0, 0, 0, 0, 0, 0, 'Imported agrivoltaic sensor data')

print("Importing Control Sensor Data")
sensor_cn = pd.read_csv(r"https://agrivoltaicatlas.com/data_ref/irrigationB2control.txt")
print(sensor_cn)

# Log that control data is imported
irrData('none', 0, 0, 0, 0, 0, 0, 0, 'Imported control sensor data')

# Check if empty and backup irrigate if so
starting_time = time.localtime(time.time()).tm_hour
if sensor_av.empty:
    
    if starting_time > 6 and starting_time < 9:

        irrData('none', 0, 0, 0, 0, 0, 0, 0, 'AV dataframe is empty, backup water')

        # Initiate AV backup irrigation
        specIrr(60, 27, flow_rate_lo, 60, 'Agrivoltaic Low')
        specIrr(120, 4, flow_rate_hi, 120, 'Agrivoltaic High')
        old_water = True

if sensor_cn.empty or old_water == True:

    if starting_time > 6 and starting_time < 9:

        irrData('none', 0, 0, 0, 0, 0, 0, 0, 'CN dataframe is empty or AV dataframe was empty, backup water')

        # Initiate AV backup irrigation
        specIrr(50, 2, flow_rate_lo, 60, 'Control Low')
        specIrr(100, 3, flow_rate_hi, 120, 'Control High')
        exit()

# Extract most recent VWC values
recent_av = sensor_av[sensor_av['TIMESTAMP'] == sensor_av.iloc[sensor_av.shape[0]-1, 0]]
recent_cn = sensor_cn[sensor_cn['TIMESTAMP'] == sensor_cn.iloc[sensor_cn.shape[0]-1, 0]]

# Extract VWC readings from Pandas dataframes
vwc_av = np.array(recent_av['vwc'], dtype=np.float16)
vwc_cn = np.array(recent_cn['vwc'], dtype=np.float16)

# Set 0 or less and 1 or greater to NaN
vwc_av[vwc_av <= 0.01] = np.nan
vwc_cn[vwc_cn <= 0.01] = np.nan
vwc_av[vwc_av >= 1] = np.nan
vwc_cn[vwc_cn >= 1] = np.nan

# Extract most recent datetime
time_av = datetime.strptime(recent_av.iloc[0, 0], '%Y-%m-%d %H:%M:%S')
time_cn = datetime.strptime(recent_cn.iloc[0, 0], '%Y-%m-%d %H:%M:%S')

# Create treatment masks to subset arrays
#            [   1      2     3    4      5      6     7     8     9      10    11    12  ] <-- These are the same as port numbers at B2
av_lo_mask = [True, False, True, False, False, True, False, True, True, False, True, False]
av_hi_mask = [False, True, False, True, True, False, True, False, False, True, False, True]
cn_lo_mask = [False, True, False, True, True, False, True, False, False, False, False, True]
cn_hi_mask = [True, False, True, False, False, True, False, True, True, True, True, False]

# Take minimum vwc for each treatment
av_lo = np.nanmedian(vwc_av[av_lo_mask])
av_hi = np.nanmedian(vwc_av[av_hi_mask])
cn_lo = np.nanmedian(vwc_cn[cn_lo_mask])
cn_hi = np.nanmedian(vwc_cn[cn_hi_mask])

# Log that the irrigation check is running
irrData('none', av_lo, av_hi, cn_lo, cn_hi, 0, 0, 0, 'Calculated minimum values')

# -------------------------------------------------------------------- #
#                  Irrigate any treatments if needed                   #
# -------------------------------------------------------------------- #

# Check if any beds are in need of irrigation, and irrigate if they need it!

# First, check to see if the Campbell data is up to date for agrivoltaics
if abs(datetime.now() - time_av) < timedelta(hours=2):
    print('Agrivoltaic sensor readings are within 2 hours: ' + str(abs(datetime.now() - time_av)))

    # Log delta between current time and last Campbell sensor measurements
    irrData('none', av_lo, av_hi, cn_lo, cn_hi, 0, 0, 0, 'Agrivoltaic sensor readings are within 2 hours: ' + str(abs(datetime.now() - time_av)))

    # Now, check if agrivoltaic low needs irrigation
    if av_lo < thresh_lo:

        # Start flow meter
        start_counter = 1

        # Turn on AV Low for specified time
        print ("Irrigation: AGRIVOLTAIC LOW ON")
        GPIO.output(27, GPIO.LOW) # 5
        start_time = time.time()

        # Log irrigation start
        irrData('Agrivoltaic Low', av_lo, av_hi, cn_lo, cn_hi, 0, 0, 0, 'Water turned on!')

        while True:
            time.sleep(1)
            
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            if elapsed_time > 1800:
                start_counter = 0
                print("Total irrigation time: " + str(int(elapsed_time))  + " seconds")
                print("Total Pulses: " + str(int(count)))
                flow = (count / flow_rate_lo)
                print("Total irrigation volume is: %.3f Gallons" % (flow))
                
                # Append to numpy array
                irrData('Agrivoltaic Low', av_lo, av_hi, cn_lo, cn_hi, elapsed_time, count, flow, '30-minute safety shutoff reached before 30 gallons')
                
                count = 0
                break
            elif (count / flow_rate_lo) >= irr_vol:
                start_counter = 0
                print("Total irrigation time: " + str(int(elapsed_time))  + " seconds")
                print("Total Pulses: " + str(int(count)))
                flow = (count / flow_rate_lo)
                print("Total irrigation volume is: %.3f Gallons" % (flow))
                
                # Append to numpy array
                irrData('Agrivoltaic Low', av_lo, av_hi, cn_lo, cn_hi, elapsed_time, count, flow, '30 gallons delivered successfully')
                
                count = 0
                break

        print ("Irrigation: AGRIVOLTAIC LOW OFF")
        GPIO.output(27, GPIO.HIGH) #5

    # Now, check if agrivoltaic high needs irrigation
    if av_hi < thresh_hi:

        # Start flow meter
        start_counter = 1

        # Turn on AV Low for specified time
        print ("Irrigation: AGRIVOLTAIC HIGH ON")
        GPIO.output(4, GPIO.LOW) #3
        start_time = time.time()

        # Log irrigation start
        irrData('Agrivoltaic High', av_lo, av_hi, cn_lo, cn_hi, 0, 0, 0, 'Water turned on!')

        while True:
            time.sleep(1)
            
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            if elapsed_time > 1800:
                start_counter = 0
                print("Total irrigation time: " + str(int(elapsed_time))  + " seconds")
                print("Total Pulses: " + str(int(count)))
                flow = (count / flow_rate_hi)
                print("Total irrigation volume is: %.3f Gallons" % (flow))
                
                # Append to numpy array
                irrData('Agrivoltaic High', av_lo, av_hi, cn_lo, cn_hi, elapsed_time, count, flow, '30-minute safety shutoff reached before 30 gallons')
                
                count = 0
                break
            elif (count / flow_rate_hi) >= irr_vol:
                start_counter = 0
                print("Total irrigation time: " + str(int(elapsed_time))  + " seconds")
                print("Total Pulses: " + str(int(count)))
                flow = (count / flow_rate_hi)
                print("Total irrigation volume is: %.3f Gallons" % (flow))
                
                # Append to numpy array
                irrData('Agrivoltaic High', av_lo, av_hi, cn_lo, cn_hi, elapsed_time, count, flow, '30 gallons delivered successfully')
                
                count = 0
                break

        print ("Irrigation: AGRIVOLTAIC HIGH OFF")
        GPIO.output(4, GPIO.HIGH) #3

else:
    # Check time since last sensor data updated
    older_time = abs(datetime.now() - time_av)
    print('Agrivoltaic sensor readings are older than 2 hours: ' + str(older_time))

    # Log delta between current time and last Campbell sensor measurements
    irrData('none', av_lo, av_hi, cn_lo, cn_hi, 0, 0, 0, 'Agrivoltaic sensor readings are older than 2 hours: ' + str(abs(datetime.now() - time_av)))

    # Go to backup irrigation if data are a day (or two, three, four, etc) old
    if (older_time % timedelta(days=1)) <= timedelta(hours=2) and (older_time % timedelta(days=1)) > timedelta(hours=0):
        specIrr(60, 27, flow_rate_lo, 60, 'Agrivoltaic Low')
        specIrr(120, 4, flow_rate_hi, 120, 'Agrivoltaic High')
        old_water = True

# Check to see if the Campbell data is up to date for control
if abs(datetime.now() - time_cn) < timedelta(hours=2):
    print('Control sensor readings are within 2 hours: ' + str(abs(datetime.now() - time_cn)))

    # Log delta between current time and last Campbell sensor measurements
    irrData('none', av_lo, av_hi, cn_lo, cn_hi, 0, 0, 0, 'Control sensor readings are within 2 hours: ' + str(abs(datetime.now() - time_cn)))

    # Now, check if control low needs irrigation
    if cn_lo < thresh_lo:

        # Start flow meter
        start_counter = 1

        # Turn on CN Low for specified time
        print ("Irrigation: CONTROL LOW ON")
        GPIO.output(2, GPIO.LOW) # 1
        start_time = time.time()

        # Log irrigation start
        irrData('Control Low', av_lo, av_hi, cn_lo, cn_hi, 0, 0, 0, 'Water turned on!')

        while True:
            time.sleep(1)
            
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            if elapsed_time > 1800:
                start_counter = 0
                print("Total irrigation time: " + str(int(elapsed_time))  + " seconds")
                print("Total Pulses: " + str(int(count)))
                flow = (count / flow_rate_lo)
                print("Total irrigation volume is: %.3f Gallons" % (flow))
                
                # Append to numpy array
                irrData('Control Low', av_lo, av_hi, cn_lo, cn_hi, elapsed_time, count, flow, '30-minute safety shutoff reached before 30 gallons')
                
                count = 0
                break
            elif (count / flow_rate_lo) >= irr_vol:
                start_counter = 0
                print("Total irrigation time: " + str(int(elapsed_time))  + " seconds")
                print("Total Pulses: " + str(int(count)))
                flow = (count / flow_rate_lo)
                print("Total irrigation volume is: %.3f Gallons" % (flow))
                
                # Append to numpy array
                irrData('Control Low', av_lo, av_hi, cn_lo, cn_hi, elapsed_time, count, flow, '30 gallons delivered successfully')
                
                count = 0
                break

        print ("Irrigation: CONTROL LOW OFF")
        GPIO.output(2, GPIO.HIGH) #1

    # Now, check if control high needs irrigation
    if cn_hi < thresh_hi:

        # Start flow meter
        start_counter = 1

        # Turn on CN Low for specified time
        print ("Irrigation: CONTROL HIGH ON")
        GPIO.output(3, GPIO.LOW) #2
        start_time = time.time()

        # Log irrigation start
        irrData('Control High', av_lo, av_hi, cn_lo, cn_hi, 0, 0, 0, 'Water turned on!')

        while True:
            time.sleep(1)
            
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            if elapsed_time > 1800:
                start_counter = 0
                print("Total irrigation time: " + str(int(elapsed_time))  + " seconds")
                print("Total Pulses: " + str(int(count)))
                flow = (count / flow_rate_hi)
                print("Total irrigation volume is: %.3f Gallons" % (flow))
                
                # Append to numpy array
                irrData('Control High', av_lo, av_hi, cn_lo, cn_hi, elapsed_time, count, flow, '30-minute safety shutoff reached before 30 gallons')
                
                count = 0
                break
            elif (count / flow_rate_hi) >= irr_vol:
                start_counter = 0
                print("Total irrigation time: " + str(int(elapsed_time))  + " seconds")
                print("Total Pulses: " + str(int(count)))
                flow = (count / flow_rate_hi)
                print("Total irrigation volume is: %.3f Gallons" % (flow))
                
                # Append to numpy array
                irrData('Control High', av_lo, av_hi, cn_lo, cn_hi, elapsed_time, count, flow, '30 gallons delivered successfully')
                
                count = 0
                break

        print ("Irrigation: CONTROL HIGH OFF")
        GPIO.output(3, GPIO.HIGH) #2

else:
    # Check time since last sensor data updated
    older_time = abs(datetime.now() - time_av)
    print('Control sensor readings are older than 2 hours: ' + str(older_time))

    # Log delta between current time and last Campbell sensor measurements
    irrData('none', av_lo, av_hi, cn_lo, cn_hi, 0, 0, 0, 'Control sensor readings are older than 2 hours: ' + str(abs(datetime.now() - time_cn)))

    # Go to backup irrigation if data are a day (or two, three, four, etc) old
    if (old_water):
        specIrr(50, 2, flow_rate_lo, 60, 'Control Low')
        specIrr(100, 3, flow_rate_hi, 120, 'Control High')

# Reset GPIO settings
GPIO.cleanup()
