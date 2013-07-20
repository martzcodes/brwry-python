from flask import Flask, render_template, url_for, jsonify, request
from livetemp import LiveTemp
from device import Device
from archive import ArchiveData
from pidcontrol import PIDControl
import json
import time
import os
os.chdir("/home/pi/brwry/")

config = json.loads(open('config.dat').read())

t = LiveTemp(config)
t.start()

h = Device(config['heats'])
h.allOff()
p = Device(config['pumps'])
p.allOff()
v = Device(config['valves'])
v.allOff()

a = ArchiveData(config,t,h,p,v)
a.start()

c = PIDControl(config,t,h,p)
c.start()

app = Flask(__name__)

if config['archiving'] == "True":
	a.resume()

def updateConfig():
	with open('config.dat','w') as outfile:
		json.dump(config,outfile)
	t.updateConfig(config)
	a.updateConfig(config)
	c.updateConfig(config)


@app.route('/_allOff')
def allOff():
	h.allOff()
	p.allOff()
	for ind, target in enumerate(config['targets']):
		config['targets'].pop(ind)
	print "All Off"

@app.route('/')
def brwry_main():
	return render_template('main_page.html')

@app.route('/about')
def brwry_about():
	return render_template('about.html')

@app.route('/_liveTempRequest')
def liveTempRequest():
	return jsonify(result=t.getCurTemp(),heat=h.getCurStatus(),pump=p.getCurStatus(),valve=v.getCurStatus(),targets=config['targets'])

@app.route('/_chartRequest')
def chartRequest():
	try:
		liveData = json.loads(open(config['storage']+'live.dat').read())
	except:
		liveData = []

	liveOut = {}

	for data in liveData:
		for key in data:
			if key != 'timestamp':
				try:
					liveOut[key]["data"].append({"x":data['timestamp'],"y":data[key]})
				except:
					liveOut[key] = {"name":key,"data":[{"x":data['timestamp'],"y":data[key]}]}

	arcOut = {}
	if config['brwInfo']['brwDate'] != '':
		brwFile = config['brwInfo']['brwDate']+'-'+config['brwInfo']['brwr']+'-'+config['brwInfo']['brwName']+'.brw'
		try:
			archiveData = json.loads(open(config['storage']+brwFile).read())
		except:
			archiveData = []
		for data in archiveData['archive']:
			for key in data:
				if key != 'timestamp':
					for sensor in config['sensors']:
						if key == sensor['sensorName']:
							try:
								arcOut[key]["data"].append({"x":data['timestamp'],"y":data[key]})
							except:
								arcOut[key] = {"name":key,"type":"sensor","data":[{"x":data['timestamp'],"y":data[key]}]}
					for heat in config['heats']:
						if key == heat['deviceName']:
							try:
								arcOut[key]["data"].append({"x":data['timestamp'],"y":data[key]})
							except:
								arcOut[key] = {"name":key,"type":"heat","data":[{"x":data['timestamp'],"y":data[key]}]}
					for pump in config['pumps']:
						if key == pump['deviceName']:
							try:
								arcOut[key]["data"].append({"x":data['timestamp'],"y":data[key]})
							except:
								arcOut[key] = {"name":key,"type":"pump","data":[{"x":data['timestamp'],"y":data[key]}]}
					for valve in config['valves']:
						if key == valve['deviceName']:
							try:
								arcOut[key]["data"].append({"x":data['timestamp'],"y":data[key]})
							except:
								arcOut[key] = {"name":key,"type":"valve","data":[{"x":data['timestamp'],"y":data[key]}]}

	return jsonify(live=liveOut,arch=arcOut)

	

@app.route('/_configRequest')
def configRequest():
	return jsonify(heat=config['heats'],pump=config['pumps'],sensor=config['sensors'],valve=config['valves'])

@app.route('/_existingBrw')
def existingBrw():
	return jsonify(brwName=config['brwInfo']['brwName'],brwr=config['brwInfo']['brwr'],brwDate=config['brwInfo']['brwDate'],paused=config['paused'])

@app.route('/configure')
def brwry_config():
	return render_template('configure.html')

@app.route('/_fullConfig')
def fullConfig():
	return jsonify(config=config)

@app.route('/_removeTarget')
def removeTarget():
	return True

@app.route('/_startBrw', methods=['POST'])
def startBrw():
	config['brwInfo'] = {
		"brwName":request.json['brwName'],
		"brwr":request.json['brwr'],
		"brwDate":str(int(time.time()))
	}
	config['archiving']="True"
	config['paused']
	updateConfig()
	a.brwChange(config['brwInfo'])
	a.resume()
	return jsonify(result=config['brwInfo'])

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
	for ind, target in enumerate(config['targets']):
		if target['device'] == request.json['device']:
			config['targets'].pop(ind)
	targetWrite = {
		"device":request.json['device'],
		"sensor":request.json['sensor'],
		"target":request.json['target']
	}
	config['targets'].append(targetWrite)
	c.updateTargets(config['targets'])
	return "Success"
 
@app.route('/_pauseBrw')
def pauseBrw():
	a.pause()
	config['paused']="True"
	updateConfig()
	return "Success"
 
@app.route('/_endBrw')
def endBrw():
	h.allOff()
	p.allOff()
	v.allOff()
	a.pause()
	config['brwInfo'] = {
		"brwName":"",
		"brwr":"",
		"brwDate":""
	}
	config['archiving']="False"
	config['paused']="True"
	config['targets'] = []
	updateConfig()
	c.updateTargets(config['targets'])
	return "Success"
 
@app.route('/_resumeBrw')
def resumeBrw():
	config['paused']="False"
	configUpdate()
	a.resume()
	return "Success"


if __name__ == '__main__':
	app.run(host='0.0.0.0',port=80,debug=True)
