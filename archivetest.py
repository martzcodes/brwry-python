"""
I made this file to test why the live data stream was so slow.
Even with time.sleep(1) off I was getting inconsistent times, between 1 and 3 seconds
"""

import time
import json

config = json.loads(open('config.dat').read())

tempDir = '/sys/bus/w1/devices/'
oldtime = 0
td = 3

while True:
    newtime = time.time()
    if newtime >= td+oldtime:
        oldtime = newtime
        liveDataWrite = {"timestamp":time.time()}
        for sensor in config['sensors']:
            try:
                f = open(tempDir + sensor['sensorAddress'] + "/w1_slave", 'r')
            except IOError as e:
                print "Error: " + sensor['sensorName'] + " does not exist."

            lines=f.readlines()
            f.close()
            crcLine=lines[0]
            tempLine=lines[1]
            result_list = tempLine.split("=")

            temp = float(result_list[-1])/1000
            temp = temp + sensor["correctionFactor"]

            if crcLine.find("NO") > -1:
                temp = -999

            liveDataWrite[str(sensor['sensorName'])] = temp

        liveData = json.loads(open('live.dat').read())
        if len(liveData) >= 100:
        	liveData.pop(0)
    
        liveData.append(liveDataWrite)

        with open('live.dat','w') as outfile:
         	json.dump(liveData,outfile)

        #if self.archiveCount >= 30:
        #	archiveData = json.loads(open('archive.dat').read())

        print time.time()

        #time.sleep(1)