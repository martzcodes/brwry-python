import RPi.GPIO as io

io.setwarnings(False)
io.setmode(io.BCM)
 
class Device:
    def __init__(self,devices):
        self.devices = devices
        for device in devices:
            io.setup(int(device['gpioPIN']),io.OUT)
            io.output(int(device['gpioPIN']),False)
 
    def deviceOn(self,pin):
        for device in self.devices:
            if device['gpioPIN'] == pin:
                io.output(int(pin),True)
            else:
                print "Does Not Match Existing Device"
 
    def deviceOff(self,pin):
        for device in self.devices:
            if device['gpioPIN'] == pin:
                io.output(int(pin),False)
            else:
                print "Does Not Match Existing Device"

    def updateDevices(self,devices):
        self.devices = devices
 
    def getCurStatus(self):
        curStatus = {}
        for device in self.devices:
            curStatus[str(device['deviceName'])] = io.input(device['gpioPIN'])

        return curStatus
 
    def deviceStatus(self,pin):
        #note: checking the input of an output pin is permitted
        return io.input(int(pin))
 
    def allOff(self):
        for device in self.devices:
            io.output(int(device['gpioPIN']),False)
