from flask import Flask, render_template, url_for, jsonify, request
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

a = ArchiveData(brwInfo,t,h,p,Targets)
a.start()

app = Flask(__name__)

@app.route('/')
def brwry_main():
	return render_template('main_page.html')

@app.route('/about')
def brwry_about():
	return render_template('about.html')

@app.route('/_liveTempRequest')
def liveTempRequest():
	return jsonify(result=t.getCurTemp())

@app.route('/configure')
def brwry_config():
	return render_template('configure.html',config=config)


if __name__ == '__main__':
	app.run(host='0.0.0.0',port=8080)
