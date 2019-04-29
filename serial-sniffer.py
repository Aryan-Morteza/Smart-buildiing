import serial
import sqlite3
import datetime
import sys
import os
from time import sleep
import struct
from thread import *

try:
	baud_rate = 9600 				#whatever baudrate you are listening to
	com_port1 = '/dev/ttyUSB0' 		#replace with your first com port path
	arduino = serial.Serial(com_port1, baud_rate)
except Exception as e:
	if str(e) == "[Errno 2] could not open port /dev/ttyUSB0: [Errno 2] No such file or directory: '/dev/ttyUSB0'":
		print "No port avalable, trying another port..."
		baud_rate = 9600 				#whatever baudrate you are listening to
		com_port1 = '/dev/ttyUSB1' 		#replace with your first com port path
		arduino = serial.Serial(com_port1, baud_rate)
relay_flag = 0
SQLITE_THREADSAFE = 1
db = sqlite3.connect('Data-set.db',check_same_thread=False)
print "Opened Database Successfully";
db.commit()
sleep(5)
cnt = 0
f = True
g = True
def RelayFeedThread(f,g,arduino): 
    while True:
		try:
			os.system("cp /home/wcl-lab/input /home/wcl-lab/input1") 
			sleep(3)
			f1 = open("/home/wcl-lab/input1", "r+")
			x = f1.read()
			f1.close()	
			if x:
				if int(x) == 1 and f == True:
					data = arduino.write(struct.pack('>B', 1))
					print "Receiving from relay board: ON"
					f = False
					g = True
				if int(x) == 0 and g == True:
					data = arduino.write(struct.pack('>B', 0))
					print "Receiving from relay board: OFF"
					g = False	
					f = True
		except Exception as msg:
			err = msg.message
			print err 
			print msg
			sleep(2)
			arduino = serial.Serial('/dev/ttyACM0' ,9600)
			print "Enter Exception"							
			pass		

while True:
	if relay_flag == 1:
		print "Relay thread started..."
		start_new_thread(RelayFeedThread ,(True,True,arduino))	
		relay_flag = 0
	try:
		arduino.flushInput()
		serial_out = arduino.readline()
		#print serial_out
		data = serial_out.split("-")
		if len(data[0]) < 2 and len(data[1]) < 3 and int(data[1]) != 0:
			sql=(int(data[0]),int(data[1]),int(data[2]),datetime.datetime.now())
			db.execute('''INSERT INTO DATA VALUES(?,?,?,?)''',sql)
			db.commit()	
			print data[0],data[1],data[2]
	except Exception as e:
		cnt += 1
		print e.message
		print cnt
		print "enter exception"
		print "Nothing to receive..."
		sleep(1)
		pass
		

