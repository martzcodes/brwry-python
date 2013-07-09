import threading
import time

class Temp(threading.Thread):

    def __init__(self, fileName):
        threading.Thread.__init__(self)
        self.tempDir = '/sys/bus/w1/devices/'
        self.fileName = fileName
        self.currentTemp = -999
        self.correctionFactor = 0
        self.enabled = True
        self._stop = threading.Event()

    def stop(self):
        print "STOP CALLED"
        self._stop.set()
        print "STOP SET"

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        while not self._stop.isSet():
            if self.isEnabled():
                try:
                    f = open(self.tempDir + self.fileName + "/w1_slave", 'r')
                except IOError as e:
                    print "Error: File " + self.tempDir + self.fileName + "/w1_slave does not exist."
                    return;

                lines=f.readlines()
                crcLine=lines[0]
                tempLine=lines[1]
                result_list = tempLine.split("=")

                temp = float(result_list[-1])/1000
                temp = temp + self.correctionFactor

                if crcLine.find("NO") > -1:
                    temp = -999

                self.currentTemp = temp

            time.sleep(1)

    def getCurrentTemp(self):
        return self.currentTemp

    def setEnabled(self, enabled):
        self.enabled = enabled

    def isEnabled(self):
        return self.enabled
