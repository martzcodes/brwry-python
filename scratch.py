#This is my scratch file... don't mind it.

from livetemp import LiveTemp
from device import Device
from archive import ArchiveData
import json
import time

config = json.loads(open('config.dat').read())

t = LiveTemp()
t.start()

h = Device(config['heats'])
h.allOff()
p = Device(config['pumps'])
p.allOff()

#temporary brwInfo
brwInfo = {
	"brwName":"Test Brew",
	"brwr":"Matt",
	"brwDate":time.time()
}

Targets = {}

a = ArchiveData(brwInfo=brwInfo,Temps=t,Heats=h,Pumps=p,Targets=Targets)
a.start()