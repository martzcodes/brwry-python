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

d = Device(config)
d.allOff()

a = ArchiveData(config,t,d)
a.start()

c = PIDControl(config,t,d)
c.start()

app = Flask(__name__)

if config['archiving'] == "True":
	a.resume()

def updateConfig():
	with open('config.dat','w') as outfile:
		json.dump(config,outfile)
	t.updateConfig(config)
	a.updateConfig(config)
	d.updateDevices(config)
	c.updateConfig(config)


@app.route('/_allOff')
def allOff():
	d.allOff()
	for ind, target in enumerate(config['targets']):
		config['targets'].pop(ind)
	print "All Off"
	return "Success"

@app.route('/')
def brwry_main():
	return render_template('main_page.html')

@app.route('/about')
def brwry_about():
	return render_template('about.html')

@app.route('/archives')
def brwry_archives():
	return render_template('archives.html')

@app.route('/_liveTempRequest')
def liveTempRequest():
	return jsonify(result=t.getCurTemp(),
		heat=d.getCurStatus('heats'),
		pump=d.getCurStatus('pumps'),
		valve=d.getCurStatus('valves'),
		targets=config['targets'])

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
	availSensors = os.listdir('/sys/bus/w1/devices')
	for ind, f in enumerate(availSensors):
		if f == 'w1_bus_master1':
			availSensors.pop(ind)
	return jsonify(config=config,availSensors=availSensors)
'''
@app.route('/_removeTarget')
def removeTarget():
	return True
'''
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
				d.deviceOn(heat['gpioPIN'])
			else:
				d.deviceOff(heat['gpioPIN'])
				for ind, target in enumerate(Targets):
					if target['device'] == request.json['deviceName']:
						Targets.pop(ind)
	for pump in config['pumps']:
		if pump['deviceName'] == request.json['deviceName']:
			if request.json['onOff'] == "ON":
				d.deviceOn(pump['gpioPIN'])
			else:
				d.deviceOff(pump['gpioPIN'])
				for ind, target in enumerate(Targets):
					if target['device'] == request.json['deviceName']:
						Targets.pop(ind)
	for valve in config['valves']:
		if valve['deviceName'] == request.json['deviceName']:
			if request.json['onOff'] == "ON":
				d.deviceOn(valve['gpioPIN'])
			else:
				d.deviceOff(valve['gpioPIN'])
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

@app.route('/_postConfig', methods=['POST'])
def postConfig():
	if request.json['btnType'] == "add":
		if request.json['updateData']['what'].find('Sensor') > -1:
			config['sensors'].append({"sensorName":request.json['updateData']['sensorName'],
				"sensorAddress":request.json['updateData']['sensorAddress'],
				"correctionFactor":float(request.json['updateData']['correctionFactor'])})
		elif request.json['updateData']['what'].find('Heat') > -1:
			if request.json['updateData']['sensors'] == None:
				config['heats'].append({"deviceName":request.json['updateData']['deviceName'],
					"gpioPIN":int(request.json['updateData']['gpioPIN']),
					"sensors":["None"]})
			else:
				config['heats'].append({"deviceName":request.json['updateData']['deviceName'],
					"gpioPIN":int(request.json['updateData']['gpioPIN']),
					"sensors":request.json['updateData']['sensors']})
			for ind, avail in enumerate(config['gpioPINs']['available']):
				if avail == int(request.json['updateData']['gpioPIN']):
					config['gpioPINs']['available'].pop(ind)
					config['gpioPINs']['unavailable'].append(int(request.json['updateData']['gpioPIN']))
		elif request.json['updateData']['what'].find('Pump') > -1:
			if request.json['updateData']['sensors'] is None:
				config['pumps'].append({"deviceName":request.json['updateData']['deviceName'],
					"gpioPIN":int(request.json['updateData']['gpioPIN']),
					"sensors":["None"]})
			else:
				config['pumps'].append({"deviceName":request.json['updateData']['deviceName'],
					"gpioPIN":int(request.json['updateData']['gpioPIN']),
					"sensors":request.json['updateData']['sensors']})
			for ind, avail in enumerate(config['gpioPINs']['available']):
				if avail == int(request.json['updateData']['gpioPIN']):
					config['gpioPINs']['available'].pop(ind)
					config['gpioPINs']['unavailable'].append(int(request.json['updateData']['gpioPIN']))
		elif request.json['updateData']['what'].find('Valve') > -1:
			config['valves'].append({"deviceName":request.json['updateData']['deviceName'],
				"gpioPIN":int(request.json['updateData']['gpioPIN'])})
			for ind, avail in enumerate(config['gpioPINs']['available']):
				if avail == int(request.json['updateData']['gpioPIN']):
					config['gpioPINs']['available'].pop(ind)
					config['gpioPINs']['unavailable'].append(int(request.json['updateData']['gpioPIN']))
	else:
		if request.json['updateData']['what'].find('sens') > -1:
			for ind, val in enumerate(config['sensors']):
				if val['sensorName'] == request.json['updateData']['oldName']:
					for device in config['heats']:
						for dind, dval in enumerate(device['sensors']):
							if dval == request.json['updateData']['oldName']:
								if request.json['btnType'] == "delete":
									device['sensors'].pop(dind)
								else:
									device['sensors'][dind] = request.json['updateData']['sensorName']
					for device in config['pumps']:
						for dind, dval in enumerate(device['sensors']):
							if dval == request.json['updateData']['oldName']:
								if request.json['btnType'] == "delete":
									device['sensors'].pop(dind)
								else:
									device['sensors'][dind] = request.json['updateData']['sensorName']
					if request.json['btnType'] == "delete":
						config['sensors'].pop(ind)
					else:
						config['sensors'][ind]['sensorName'] = request.json['updateData']['sensorName']
						config['sensors'][ind]['sensorAddress'] = request.json['updateData']['sensorAddress']
						config['sensors'][ind]['correctionFactor'] = float(request.json['updateData']['correctionFactor'])

		elif request.json['updateData']['what'].find('heat') > -1:
			for ind, val in enumerate(config['heats']):
				if val['deviceName'] == request.json['updateData']['oldName']:
					if request.json['btnType'] == "delete":
						d.deviceOff(int(request.json['updateData']['gpioPIN']))
						config['heats'].pop(ind)
						for dind, avail in enumerate(config['gpioPINs']['unavailable']):
							if avail == int(request.json['updateData']['gpioPIN']):
								config['gpioPINs']['unavailable'].pop(ind)
								config['gpioPINs']['available'].append(int(request.json['updateData']['gpioPIN']))
					else:
						config['heats'][ind]['deviceName'] = request.json['updateData']['deviceName']
						config['heats'][ind]['gpioPIN'] = int(request.json['updateData']['gpioPIN'])
						config['heats'][ind]['sensors'] = request.json['updateData']['sensors']

		elif request.json['updateData']['what'].find('pump') > -1:
			for ind, val in enumerate(config['pumps']):
				if val['deviceName'] == request.json['updateData']['oldName']:
					if request.json['btnType'] == "delete":
						d.deviceOff(int(request.json['updateData']['gpioPIN']))
						config['pumps'].pop(ind)
						for dind, avail in enumerate(config['gpioPINs']['unavailable']):
							if avail == int(request.json['updateData']['gpioPIN']):
								config['gpioPINs']['unavailable'].pop(ind)
								config['gpioPINs']['available'].append(int(request.json['updateData']['gpioPIN']))
					else:
						config['pumps'][ind]['deviceName'] = request.json['updateData']['deviceName']
						config['pumps'][ind]['gpioPIN'] = int(request.json['updateData']['gpioPIN'])
						config['pumps'][ind]['sensors'] = request.json['updateData']['sensors']

		elif request.json['updateData']['what'].find('valve') > -1:
			for ind, val in enumerate(config['valves']):
				if val['deviceName'] == request.json['updateData']['oldName']:
					if request.json['btnType'] == "delete":
						d.deviceOff(int(request.json['updateData']['gpioPIN']))
						config['valves'].pop(ind)
						for dind, avail in enumerate(config['gpioPINs']['unavailable']):
							if avail == int(request.json['updateData']['gpioPIN']):
								config['gpioPINs']['unavailable'].pop(ind)
								config['gpioPINs']['available'].append(int(request.json['updateData']['gpioPIN']))
					else:
						config['valves'][ind]['deviceName'] = request.json['updateData']['deviceName']
						config['valves'][ind]['gpioPIN'] = int(request.json['updateData']['gpioPIN'])
		elif request.json['updateData']['what'] == 'storage':
			config['storage'] = request.json['updateData']['storage']
	config['gpioPINs']['available'] = sorted(config['gpioPINs']['available'])
	config['gpioPINs']['unavailable'] = sorted(config['gpioPINs']['unavailable'])

	updateConfig()
	return render_template('configure.html')
 
@app.route('/_pauseBrw')
def pauseBrw():
	a.pause()
	config['paused']="True"
	updateConfig()
	return "Success"
 
@app.route('/_endBrw')
def endBrw():
	d.allOff()
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
	updateConfig()
	a.resume()
	return "Success"

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=80,debug=True)
