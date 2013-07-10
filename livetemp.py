import threading
import time
import json

config = json.loads(open('config.dat').read())

class LiveTemp(threading.Thread):
    #def __init__(self, brwName):
    def __init__(self):
        threading.Thread.__init__(self)
        self.tempDir = '/sys/bus/w1/devices/'
        # self.brwName = brwName
        self._stop = threading.Event()
        self._pause = False
        self.curTemp = {}
        self.td = 3
        self.oldtime = 0
        self.liveDataLength = 100
        # self.archiveCount = 30

    def stop(self):
        self._stop.set()
        print "STOP SET"

    def setTD(self,TD):
    	self.td = TD

    def setLDL(self,LDL):
    	self.liveDataLength = LDL

    def pause(self):
        self._pause = True

    def unpause(self):
    	self._pause = False

    def stopped(self):
        return self._stop.isSet()

    def paused(self):
        return self._pause

    def getCurTemp(self):
        return self.curTemp

    def run(self):
        while not self._stop.isSet():
            if not self.paused():
                newtime = time.time()
                if newtime >= self.td+self.oldtime:
                    self.oldtime = newtime
                    liveDataWrite = {"timestamp":time.time()}
                    for sensor in config['sensors']:
                        try:
                            f = open(self.tempDir + sensor['sensorAddress'] + "/w1_slave", 'r')
                        except IOError as e:
                            print "Error: " + sensor['sensorName'] + " does not exist."
                            return;

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

                try:
                	liveData = json.loads(open('live.dat').read())
                except:
                	liveData = []

                while len(liveData) > self.liveDataLength:
                	liveData.pop(0)
                if len(liveData) == self.liveDataLength:
                    liveData.pop(0)
            
                liveData.append(liveDataWrite)
                self.curTemp = liveDataWrite

                with open('live.dat','w') as outfile:
                    json.dump(liveData,outfile)

                #if self.archiveCount >= 30:
                #	archiveData = json.loads(open('archive.dat').read())