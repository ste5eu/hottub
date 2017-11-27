#!/usr/bin/python
from gpiozero import LED, Button
from signal import pause
from time import sleep

blue = LED(27)
	
	# Initialise the buttons

def say_hello():
    print("Hello!")
    blue.on()

def say_goodbye():
    print("Goodbye!")
    blue.off()

button = Button(21)

button.when_pressed = say_hello
button.when_released = say_goodbye
print 'Started'

while True:
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
			
	sleep(1)
