import threading
import time
import json

class PIDControl(threading.Thread):

	def __init__(self,config,t,d):
		threading.Thread.__init__(self)
		self.tempDir = '/sys/bus/w1/devices/'
		self._stop = threading.Event()
		self._pause = True
		self.t = t
		self.d = d
		self.config = config
		self.curTemp = {}
		self.dT = 1 #degree F
		self.targets = config['targets']
		self.interval = 10
		self.oldtime = 0
		self.liveDataLength = 100

	def stop(self):
		self._stop.set()
		print "STOP SET"

	def setInterval(self,TD):
		self.interval = TD

	def pause(self):
		self._pause = True

	def resume(self):
		self._pause = False

	def stopped(self):
		return self._stop.isSet()

	def paused(self):
		return self._pause

	def updateConfig(self,config):
		self.config = config

	def updateTargets(self,targets):
		self.targets = targets
		self._pause = False

	def run(self):
		while not self._stop.isSet():
			if not self.paused():
				newtime = time.time()
				if newtime >= self.interval+self.oldtime:
					self.oldtime = newtime
					
					if len(self.targets) == 0:
						self._pause = True
					else:
						self.curTemp = self.t.getCurTemp()
						for target in self.targets:
							for heat in self.config['heats']:
								if heat['deviceName'] == target['device']:
									testval = float(target['target'])+float(self.dT)
									if self.curTemp[target['sensor']] >= testval:
										#Turn Element Off
										self.d.deviceOff(heat['gpioPIN'])
									else:
										#Turn Element On
										self.d.deviceOn(heat['gpioPIN'])

							for pump in self.config['pumps']:
								if pump['deviceName'] == target['device']:
									if self.curTemp[target['sensor']] >= float(target['target']):
										#Turn Pump On
										self.d.deviceOn(pump['gpioPIN'])
									else:
										#Turn Pump Off
										self.d.deviceOff(pump['gpioPIN'])




