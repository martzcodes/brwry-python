from flask import Flask, render_template, url_for, jsonify, request
from livetemp import LiveTemp
from device import Device
from archive import ArchiveData
from pidcontrol import PIDControl
import json
import time

config = json.loads(open('config.dat').read())

t = LiveTemp()
t.start()

h = Device(config['heats'])
h.allOff()
p = Device(config['pumps'])
p.allOff()
v = Device(config['valves'])
v.allOff()

#temporary brwInfo
brwInfo = {
	"brwName":"Test Brew",
	"brwr":"Matt",
	"brwDate":str(int(time.time()))
}

Targets = []

a = ArchiveData(brwInfo,t,h,p,v,Targets,config['storage'])
a.start()

c = PIDControl(t,h,p)
c.start()

app = Flask(__name__)


@app.route('/_allOff')
def allOff():
	h.allOff()
	p.allOff()
	for ind, target in enumerate(Targets):
		Targets.pop(ind)
	print "All Off"

@app.route('/')
def brwry_main():
	return render_template('main_page.html')

@app.route('/about')
def brwry_about():
	return render_template('about.html')

@app.route('/_liveTempRequest')
def liveTempRequest():
	return jsonify(result=t.getCurTemp(),heat=h.getCurStatus(),pump=p.getCurStatus(),valve=v.getCurStatus(),targets=Targets)

@app.route('/_configRequest')
def configRequest():
	return jsonify(heat=config['heats'],pump=config['pumps'],sensor=config['sensors'],valve=config['valves'])

@app.route('/configure')
def brwry_config():
	return render_template('configure.html',config=config)

@app.route('/_removeTarget')
def removeTarget():
	return True

@app.route('/_startBrw', methods=['POST'])
def startBrw():
	brwInfo = {
		"brwName":request.json['brwName'],
		"brwr":request.json['brwr'],
		"brwDate":str(int(time.time()))
	}
	a.brwChange(brwInfo)
	a.resume()
	return jsonify(result=brwInfo)

@app.route('/_deviceOnOff', methods=['POST'])
def deviceOnOff():
	for heat in config['heats']:
		if heat['deviceName'] == request.json['deviceName']:
			if request.json['onOff'] == "ON":
				h.deviceOn(heat['gpioPIN'])
			else:
				h.deviceOff(heat['gpioPIN'])
				for ind, target in enumerate(Targets):
					if target['device'] == request.json['deviceName']:
						Targets.pop(ind)
	for pump in config['pumps']:
		if pump['deviceName'] == request.json['deviceName']:
			if request.json['onOff'] == "ON":
				p.deviceOn(pump['gpioPIN'])
			else:
				p.deviceOff(pump['gpioPIN'])
				for ind, target in enumerate(Targets):
					if target['device'] == request.json['deviceName']:
						Targets.pop(ind)
	for valve in config['valves']:
		if valve['deviceName'] == request.json['deviceName']:
			if request.json['onOff'] == "ON":
				v.deviceOn(valve['gpioPIN'])
			else:
				v.deviceOff(valve['gpioPIN'])
	
	return "Success"
 
@app.route('/_addTarget', methods=['POST'])
def addTarget():
	for ind, target in enumerate(Targets):
		if target['device'] == request.json['device']:
			Targets.pop(ind)
	targetWrite = {
		"device":request.json['device'],
		"sensor":request.json['sensor'],
		"target":request.json['target']
	}
	Targets.append(targetWrite)
	c.updateTargets(Targets)
	return "Success"
 
@app.route('/_pauseBrw')
def pauseBrw():
	a.pause()
	print "paused"
 
@app.route('/_endBrw')
def endBrw():
	a.pause()
	h.allOff()
	p.allOff()
	v.allOff()
	Targets = []
	c.updateTargets(Targets)
	print "brew ended"
 
@app.route('/_resumeBrw')
def resumeBrw():
	a.resume()


if __name__ == '__main__':
	app.run(host='0.0.0.0',port=8080)
