import threading
import time
import RPi.GPIO as io
import json

io.setmode(io.BCM)
config = json.loads(open('config.dat').read())
 
class ArchiveData(threading.Thread):
    def __init__(self, brwInfo,Temps,Heats,Pumps,Targets):
        threading.Thread.__init__(self)
        self.tempDir = '/sys/bus/w1/devices/'
        self.brwInfo = brwInfo
        self.brwFile = str(brwInfo['brwDate'])+'-'+brwInfo['brwr']+'-'+brwInfo['brwName']+'.brw'
        self.Temps = Temps
        self.Heats = Heats
        self.Pumps = Pumps
        self.Targets = Targets
        self._stop = threading.Event()
        self._pause = True
 
    def stop(self):
        self._stop.set()
        print "STOP SET"
 
    def unpause(self):
        self._pause = False
 
    def brwChange(self,brwInfo):
        self._pause = True
        self.brwInfo = brwInfo
        self.brwFile = self.brwInfo['brwDate']+'-'+self.brwInfo['brwr']+'-'+self.brwInfo['brwName']+'.brw'
        time.sleep(5)
        self._pause = False

    def updateTargets(self,Targets):
    	self.Targets = Targets
 
    def pause(self):
        self._pause = True
 
    def stopped(self):
        return self._stop.isSet()
 
    def paused(self):
        return self._pause
 
    def run(self):
        while not self._stop.isSet():
            if not self.paused():
                try:
                    brwData = json.loads(open(self.brwFile).read())
                except:
                    brwData = {"archive":[]}
                    for info in self.brwInfo:
                        brwData[info]=self.brwInfo[info]
                archiveDataWrite = {}
                archiveDataWrite['timestamp']=time.time()

                curTemps = self.Temps.getCurTemp()
                for temp in curTemps:
                    if temp != "timestamp":
                        archiveDataWrite[temp]=curTemps[temp]

                curHeats = self.Heats.getCurStatus()
                for heat in curHeats:
                    archiveDataWrite[heat]=curHeats[heat]

                curPumps = self.Pumps.getCurStatus()
                for pump in curPumps:
                    archiveDataWrite[pump]=curPumps[pump]

                for target in self.Targets:
                    archiveDataWrite[target]=self.Targets[target]
 
                brwData['archive'].append(archiveDataWrite)
                print brwData
 
                with open(self.brwFile,'w') as outfile:
                    json.dump(brwData,outfile)
            time.sleep(60)