import threading
import time
import json

 
class ArchiveData(threading.Thread):
	def __init__(self, config,t,d):
		threading.Thread.__init__(self)
		self.tempDir = '/sys/bus/w1/devices/'
		self.brwInfo = config['brwInfo']
		self.brwDir = config['storage']
		self.brwFile = str(self.brwInfo['brwDate'])+'-'+self.brwInfo['brwr']+'-'+self.brwInfo['brwName']+'.brw'
		self.t = t
		self.d = d
		self.targets = config['targets']
		self._stop = threading.Event()
		self.oldtime = 0
		self._pause = True
		self.interval = 60
 
	def stop(self):
		self._stop.set()
		print "STOP SET"
 
	def resume(self):
		self._pause = False
 
	def brwChange(self,brwInfo):
		print "changing brew info"
		wasPaused = True
		if not self.paused():
			wasPaused = False
			self._pause = True

		self.brwInfo = brwInfo
		self.brwFile = self.brwInfo['brwDate']+'-'+self.brwInfo['brwr']+'-'+self.brwInfo['brwName']+'.brw'
		
		if not wasPaused:
			time.sleep(1)
			self._pause = False

	def updateConfig(self,config):
		self.brwInfo = config['brwInfo']
		self.brwDir = config['storage']
		self.targets = config['targets']

	def updateTargets(self,targets):
		self.targets = targets

	def setInterval(self,interval):
		self.interval = interval
 
	def pause(self):
		self._pause = True
 
	def stopped(self):
		return self._stop.isSet()
 
	def paused(self):
		return self._pause
   
	def run(self):
		while not self._stop.isSet():
			if not self.paused():
				newtime = time.time()
				if newtime >= self.interval+self.oldtime:
					self.oldtime = newtime
					try:
						brwData = json.loads(open(self.brwDir+self.brwFile).read())
					except:
						brwData = {"archive":[]}
					
					for info in self.brwInfo:
						brwData[info]=self.brwInfo[info]
						archiveDataWrite = {}
						archiveDataWrite['timestamp']=time.time()

						curTemps = self.t.getCurTemp()
						for temp in curTemps:
							if temp != "timestamp":
								archiveDataWrite[temp]=curTemps[temp]

						curHeats = self.d.getCurStatus('heats')
						for heat in curHeats:
							archiveDataWrite[heat]=curHeats[heat]

						curPumps = self.d.getCurStatus('pumps')
						for pump in curPumps:
							archiveDataWrite[pump]=curPumps[pump]

						curValves = self.d.getCurStatus('valves')
						for valve in curValves:
							archiveDataWrite[valve]=curValves[valve]

						archiveDataWrite["targets"]=[]
						for target in self.targets:
							archiveDataWrite["targets"].append(target)
		 
						brwData['archive'].append(archiveDataWrite)
		 
						with open(self.brwDir+self.brwFile,'w') as outfile:
							json.dump(brwData,outfile)