import serial
import sqlite3
import datetime
import sys
import os
from time import sleep
import struct
from thread import *

def RelayFeedThread(): 
	USB_port_quantity = 50
	baud_rate = 19200
	f = True
	g = True
	h = True
	j = True
	port = 1
	while 1:
		try:
			arduino = serial.Serial('/dev/ttyUSB' + str(port) ,baud_rate)
			print("Connection to " + '/dev/ttyUSB' + str(port) + " established succesfully!\n")
			break
		except Exception as e:
			port += 1
			if port == USB_port_quantity:
				print "There is no connected device!"
				print "We scan " + str(USB_port_quantity ) + " usb port on this baud rate: " + str(baud_rate) + ". Check the ports and arduino!"
				break
	while 1:
		try:
			os.system("cp /home/wcl-lab/input_fan /home/wcl-lab/input1") 
			os.system("cp /home/wcl-lab/input_pump /home/wcl-lab/input2") 
			sleep(3)
			f_fan = open("/home/wcl-lab/input1", "r+")
			x = f_fan.read()
			f_fan.close()	
			f_pomp = open("/home/wcl-lab/input2", "r+")
			y = f_pomp.read()
			f_pomp.close()	
			if x:
				if int(x) == 1 and f:
					data = arduino.write(struct.pack('>B', 1))
					print "Receiving from relay board: ON (Fan)"
					f = False
					g = True
				if int(x) == 0 and g:
					data = arduino.write(struct.pack('>B', 0))
					print "Receiving from relay board: OFF (Fan)"
					f = True
					g = False
			if y:		
				if int(y) == 1 and h:
					data = arduino.write(struct.pack('>B', 2))
					print "Receiving from relay board: ON (Pump)"
					h = False
					j = True
				if int(y) == 0 and j:
					data = arduino.write(struct.pack('>B', 3))
					print "Receiving from relay board: OFF (Pump)"
					h = True
					j = False
		except Exception as msg:
			if str(msg) == "write failed: [Errno 5] Input/output error":
				print "Device(Relay-board) is not connected! Please check your connections..."
				sleep(5)
			port = 1
			while 1:
				try:
					arduino = serial.Serial('/dev/ttyUSB' + str(port) ,baud_rate)
					print("Connection to " + '/dev/ttyUSB' + str(port) + " established succesfully!\n")
					f = True
					g = True
					h = True
					j = True
					break
				except Exception as e:
					port += 1
					sleep(0.5)
					print "Scaning usb port in progress...","\r",	
					if port == USB_port_quantity: port = 1						
			pass		
RelayFeedThread()
