from flask import Flask, render_template, url_for, jsonify, request
from livetemp import LiveTemp
import json

liveTemp = LiveTemp()
liveTemp.start()

config = json.loads(open('config.dat').read())

app = Flask(__name__)

@app.route('/')
def brwry_main():
	return render_template('main_page.html')

@app.route('/about')
def brwry_about():
	return render_template('about.html')

@app.route('/_liveTempRequest')
def liveTempRequest():
	return jsonify(result=liveTemp.getCurTemp())

@app.route('/configure')
def brwry_config():
	return render_template('configure.html',config=config)


if __name__ == '__main__':
	app.run(host='0.0.0.0',port=8080)
