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
I2C_ADDR  = 0x3f # I2C device address
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

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

# Temperature settingsTUB_SENSOR = ''
HEATER_SENSOR = '28-011592aeacff'
TUB_SENSOR = ''
OUTSIDE_SENSOR = ''

MAX_TEMP = 38
desired_temp = 21.0
temp_led = LED(27)
jets1_running = False
jets2_running = False
air_running = False  

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
			print line
			if line_no == 1:
				param_list = line.split(" ")
				print param_list
				index = param_list[9].find('\n')
				temp_text = param_list[9][2:index]
				temp_value = int(temp_text)/1000
				print temp_value
			line_no += 1
	return temp_value

def read_temp():
	heater_temp = read_sensor(HEATER_SENSOR)
	#tub_temp = read_sensor(TUB_SENSOR)
	#outside_temp = read_sensor(OUTSIDE_SENSOR)
	
	data = {}
	data['heater_temp'] = heater_temp
	json_data = json.dumps(data)
	
	df = open(data_filename, 'w')
	df.write(json_data)
	df.close()
	
# Button handlers
def temp_down_pressed():
	print 'Pressed'
	temp_led.on()

def temp_down_released():
	global desired_temp
	print'Released'
	temp_led.off()
	if desired_temp > 0:
		desired_temp -= 0.5
		
	print 'Desired:' + str(desired_temp)

def temp_up_released():
	global desired_temp
	if desired_temp < MAX_TEMP:
		desired_temp += 0.5

def switch_jets1():
	global jets1_running
	if jets1_running == True:
		#jets1.off()
		jets1_running = False
	else:
		#jets1.on
		jets1_running = True

def switch_jets2():
	global jets2_running
	if jets2_running == True:
		#jets1.off()
		jets2_running = False
	else:
		#jets1.on
		jets2_running = True

def switch_air():
	global air_running
	if air_running == True:
		#jets1.off()
		air_running = False
	else:
		#jets1.on
		air_running = True

def shutdown():
    check_call(['sudo', 'poweroff'])

def main():
  # Main program block
	# Initialise the relays 
	heater = LED(17)
	temp = 19
	
	# Initialise the buttons
	shutdown_button = Button(25, hold_time=2)
	shutdown_button.when_held = shutdown

	temp_down_button = Button(21)
	temp_down_button.when_released = temp_down_released
	temp_up_button = Button(20)
	temp_up_button.when_released = temp_up_released
	jets1_button = Button(7)
	jets1_button.when_released = switch_jets1
	jets2_button = Button(12)
	jets2_button.when_released = switch_jets2
	air_button = Button(16)
	air_button.when_released = switch_air
	
	
  # Initialise display
	lcd_init()

	while True:
		read_temp()
		
		data = json.load(open(data_filename))
		print(data)
	
		temp = data['heater_temp']
		print temp
		if temp < desired_temp:
			heater.on()
		
		if temp >= desired_temp:
			heater.off()

		line1_text = 'Target:' + str(desired_temp) + ' At:' + str(temp)
		line2_text = '     '
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
		#sleep(1)

if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)

