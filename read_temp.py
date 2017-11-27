#!/usr/bin/python
import json

data_filename = '/data/temp_data.json'
conf_filename = '/data/config_data.json'

with open("/sys/bus/w1/devices/28-011592aeacff/w1_slave") as f:
	line_no = 0
	temp_value = 0
	for line in f:
		print line
		if line_no == 1:
			param_list = line.split(" ")
			print param_list
			index = param_list[9].find('\n')
			temp_text = param_list[9][2:index]
			temp_value = int(temp_text)/1000
			print temp_value
		line_no += 1

	data = {}
	data['heater_temp'] = temp_value
	json_data = json.dumps(data)
	
	f = open(data_filename, 'w')
	f.write(json_data)
	f.close()