import threading
import time
import json

config = json.loads(open('config.dat').read())

class PIDControl(threading.Thread):

	def __init__(self,t,h,p):
		threading.Thread.__init__(self)
		self.tempDir = '/sys/bus/w1/devices/'
		self._stop = threading.Event()
		self._pause = True
		self.t = t
		self.h = h
		self.p = p
		self.curTemp = {}
		self.dT = 1 #degree F
		self.Targets = []
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

	def updateTargets(self,Targets):
		self.Targets = Targets
		self._pause = False

	def run(self):
		while not self._stop.isSet():
			if not self.paused():
				newtime = time.time()
				if newtime >= self.interval+self.oldtime:
					self.oldtime = newtime
					
					if len(self.Targets) == 0:
						self._pause = True
					else:
						self.curTemp = self.t.getCurTemp()
						for target in self.Targets:
							for heat in config['heats']:
								if heat['deviceName'] == target['device']:
									testval = float(target['target'])+float(self.dT)
									if self.curTemp[target['sensor']] >= testval:
										#Turn Element Off
										self.h.deviceOff(heat['gpioPIN'])
									else:
										#Turn Element On
										self.h.deviceOn(heat['gpioPIN'])

							for pump in config['pumps']:
								if pump['deviceName'] == target['device']:
									if self.curTemp[target['sensor']] >= float(target['target']):
										#Turn Pump On
										self.p.deviceOn(pump['gpioPIN'])
									else:
										#Turn Pump Off
										self.p.deviceOff(pump['gpioPIN'])




