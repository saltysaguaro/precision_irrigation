#!/bin/sh

#MY_PATH="`dirname \"$0\"`"              # relative
LOG_PATH="/home/pi/network.log"
now=$(date +"%m-%d %r")

# Which Interface do you want to check
wlan='wlan0'
# Which address do you want to ping to see if you can connect
pingip='google.com<http://google.com>'

# Perform the network check and reset if necessary
/bin/ping -c 2 -I $wlan $pingip > /dev/null 2> /dev/null
if [ $? -ge 1 ] ; then
    echo "$now Network is DOWN. Perform a reset" >> $LOG_PATH
    /sbin/ifdown $wlan
    sleep 5
    /sbin/ifup --force $wlan
    sudo service dhcpcd restart
else
    echo "$now Network is UP. Just exit the program." >> $LOG_PATH
fi