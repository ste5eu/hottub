from flask import Flask
import subprocess
import json
from pprint import pprint

app = Flask(__name__)
first_time = False

@app.route("/")
def home():
	return "Hello World"
theuptons.ddns.net

@app.route("/status")
def status():
	data = json.load(open('/data/temp_data.json'))
	return json.dumps(data)

if __name__ == "__main__":
	hostname = subprocess.check_output(["hostname", "-I"])
	app.run(host=hostname, port=80, debug=True)