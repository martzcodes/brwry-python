import RPi.GPIO as io

io.setwarnings(False)
io.setmode(io.BCM)
 
class Device:
	def __init__(self,config):
		self.config = config
		for device in self.config['gpioPINs']['unavailable']:
			io.setup(int(device),io.OUT)
			io.output(int(device),False)
		for device in self.config['gpioPINs']['available']:
			io.setup(int(device),io.OUT)
			io.output(int(device),False)
 
	def deviceOn(self,pin):
		for device in self.config['gpioPINs']['unavailable']:
			if int(device) == int(pin):
				io.output(int(pin),True)
			else:
				print "Does Not Match Existing Device"
 
	def deviceOff(self,pin):
		for device in self.config['gpioPINs']['unavailable']:
			if int(device) == int(pin):
				io.output(int(pin),False)
			else:
				print "Does Not Match Existing Device"

	def updateDevices(self,config):
		self.config = config
 
	def getCurStatus(self,devType):
		curStatus = {}
		for device in self.config[devType]:
			curStatus[str(device['deviceName'])] = io.input(int(device['gpioPIN']))
		return curStatus
 
	def deviceStatus(self,pin):
		#note: checking the input of an output pin is permitted
		return io.input(int(pin))
 
	def allOff(self):
		for device in self.config['gpioPINs']['unavailable']:
			io.output(int(device),False)
		for device in self.config['gpioPINs']['available']:
			io.output(int(device),False)
