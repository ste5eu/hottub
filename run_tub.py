#!/usr/bin/python

from gpiozero import LED, Button
from time import sleep
import json
from pprint import pprint
from signal import pause
import smbus
from subprocess import check_call

data_filename = '/data/temp_data.json'

# Define some device parameters
I2C_ADDR  = 0x3F # I2C device address
LCD_WIDTH = 20   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# Run Statuses
STARTING_UP = 10
RUNNING = 20
ERROR = 99

run_status = STARTING_UP

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

# Temperature settingsTUB_SENSOR = ''
#HEATER_SENSOR = '28-011592aeacff'
HEATER_SENSOR = '28-011592ac2bff'
TUB_SENSOR = '28-011592ac2bff'
OUTSIDE_SENSOR = '28-011592ac2bff'

# Define the GPIO Pins
#PIN_TEMP = 26
#PIN_JETS1 = 21
#PIN_JETS2 = 20
#PIN_AIR = 6


MAX_TEMP = 38
desired_temp = 21.0
heater_temp = 0.0
tub_temp = 0.0
outside_temp = 0.0

jets1 = LED(26)	# Relay 1
jets2 = LED(19) # Relay 2
air = LED(13) # Relay 3
heater = LED(6) # Relay 4
lights = LED(5) # Relay 5
pin6 = LED(11) # Relay 6
pin7 = LED(9) # Relay 7
circ_pump = LED(10) # Relay 8

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = the data
  # mode = 1 for data
  #        0 for command

  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

  # High bits
  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)

  # Low bits
  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
  # Toggle enable
  sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  sleep(E_PULSE)
  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def read_sensor(sensor_name):
	filename = "/sys/bus/w1/devices/"+sensor_name+"/w1_slave"
	with open(filename) as f:
		line_no = 0
		temp_value = 0
		for line in f:
#			print line
			if line_no == 1:
				param_list = line.split(" ")
#				print param_list
				index = param_list[9].find('\n')
				temp_text = param_list[9][2:index]
				temp_value = int(temp_text)/1000
#				print temp_value
			line_no += 1
	return temp_value

def read_temp():
	global heater_temp, tub_temp, outside_temp
	
	heater_temp = read_sensor(HEATER_SENSOR)
	tub_temp = read_sensor(TUB_SENSOR)
	outside_temp = read_sensor(OUTSIDE_SENSOR)
	
	data = {}
	data['heater_temp'] = heater_temp
	data['tub_temp'] = tub_temp
	data['outside_temp'] = outside_temp
	json_data = json.dumps(data)
	
	df = open(data_filename, 'w')
	df.write(json_data)
	df.close()
	
# Button handlers
def temp_down_pressed():
	print 'Pressed'

def temp_down_released():
	global desired_temp
	if desired_temp > 0:
		desired_temp -= 0.5
		
	print 'Desired:' + str(desired_temp)

def temp_up_released():
	global desired_temp
	if desired_temp < MAX_TEMP:
		desired_temp += 0.5

def switch_jets1():
	if jets1.is_lit == True:
		jets1.off()
	else:
		jets1.on()

def switch_jets2():
	if jets2.islit == True:
		jets2.off()
	else:
		jets2.on()

def switch_air():
	if air.is_lit == True:
		air.off()
	else:
		air.on()

def shutdown():
  check_call(['sudo', 'poweroff'])

def switch_lights():
	print "Lights"
	
def flow_stopped():
	#STOP EVERYTHING
	
	
def test_board():
	print("Test")
	
	while(True):
		heater.on()
		sleep(1)
		heater.off()
		sleep(1)	
		jets1.on()
		sleep(1)
		jets1.off()
		sleep(1)	
		jets2.on()
		sleep(1)
		jets2.off()
		sleep(1)	
		air.on()
		sleep(1)
		air.off()
		sleep(1)	
		pin5.on()
		sleep(1)
		pin5.off()
		sleep(1)	
		pin6.on()
		sleep(1)
		pin6.off()
		sleep(1)	
		pin7.on()
		sleep(1)
		pin7.off()
		sleep(1)	
		pin8.on()
		sleep(1)
		pin8.off()
		sleep(1)
		
		heater.on()
		sleep(1)
		jets1.on()
		sleep(1)
		jets2.on()
		sleep(1)
		air.on()
		sleep(1)
		pin5.on()
		sleep(1)
		pin6.on()
		sleep(1)
		pin7.on()
		sleep(1)
		pin8.on()
		sleep(1)
		heater.off()
		sleep(1)	
		jets1.off()
		sleep(1)	
		jets2.off()
		sleep(1)	
		air.off()
		sleep(1)	
		pin5.off()
		sleep(1)	
		pin6.off()
		sleep(1)	
		pin7.off()
		sleep(1)	
		pin8.off()
		sleep(1)	

def pumps_off():
	print "Pumps off"
	jets1.off()
	jets2.off()
	air.off
		
def all_stop():
	print "ALL STOP"
	heater.off()
	pumps_off()
	circ_pupm.off()
	lights.off()
	
def display_text(message_text):
	lcd_string(message_text,LCD_LINE_4)

	
def main():
	
	#test_board()
  # Main program block
	# Initialise the relays 
	temp = 19
	
	# Initialise the buttons
	flow_button = Button(8)
	flow_button.when_released = flow_stopped
	
	shutdown_button = Button(18, hold_time=2)
	shutdown_button.when_held = shutdown

	temp_down_button = Button(12)
	temp_down_button.when_released = temp_down_released
	temp_up_button = Button(16)
	temp_up_button.when_released = temp_up_released
	
	jets1_button = Button(21)
	jets1_button.when_released = switch_jets1
	
	jets2_button = Button(20)
	jets2_button.when_released = switch_jets2
	
	air_button = Button(23)
	air_button.when_released = switch_air
	
	lights_button = Button(24)
	lights_button.when_released = switch_lights
	
  # Initialise display
	lcd_init()

	# Startup routine
	display_status("Starting up ...")
		
	# Run the Circulating pump briefly
	circ_pump.on()
	sleep(2)

	# If not flowing then STOP
	if flow_button.is_pressed() == False:
		circ_pump.off()
		display_status("Error: No flow")
		run_status = ERROR
	else:
		run_status = RUNNING
					
	while True:
		read_temp()
		data = json.load(open(data_filename))
		print(data)
	
		heater_temp = data['heater_temp']
		print heater_temp
		
		if run_status == RUNNING:	
			if heater_temp < desired_temp:
				heater.on()
		
			if heater_temp >= desired_temp:
				heater.off()

			line1_text = 'Target:' + str(desired_temp) + ' At:' + str(tub_temp)
			line2_text = 'Heater:' + str(heater_temp) + ' Outside:' + str(outside_temp)
			line3_text = '30'
			line4_text = ''
	
			if (jets1_running):
				line4_text += 'Jets1 '
			else:
				line4_text += '      '
			
			if (jets2_running):
				line4_text += 'Jets2 '
			else:
				line4_text += '      '
			
			if (air_running):
				line4_text += 'Air'
			else:
				line4_text += '   '
			
			lcd_string(line1_text,LCD_LINE_1)
			lcd_string(line2_text,LCD_LINE_2)
			lcd_string(line3_text,LCD_LINE_3)	
			lcd_string(line4_text,LCD_LINE_4)
			sleep(1)

if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)

