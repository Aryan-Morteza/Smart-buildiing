#!/usr/bin/python
import os
import sys
import errno
import socket
import sqlite3
import datetime
from thread import *
from time import sleep
from simpleusbrelay import *
#############################Relay Initializing (idVendor and Product id)#################################
relay_flag = 1
try:
	idVendor = int("16c0", 16)
	idProduct = int("05df", 16)
	relaycontroller = simpleusbrelay(idVendor, idProduct)
except:
	relay_flag = 0
	print "Something Wrong with Relay Board... Check USB Connection!"
#######################################Network Initializing###############################################
Host = '192.168.47.15'   
Port = 9001 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket Created'
try:
    s.bind((Host, Port))
except socket.error as msg:
    print 'Bind Failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit() 
print 'Socket Bind Complete'
client_no = 11
s.listen(client_no)
print 'Socket Now Listening...'
##########################################Database Opening################################################
SQLITE_THREADSAFE = 1
db = sqlite3.connect('Data-set.db', check_same_thread = False)
print "Opened Database Successfully"
db.commit()
db1 = sqlite3.connect('/var/www/html/project/database/Data-set-Real-Time.db', check_same_thread = False)
print "Opened Database(Real-Time) Successfully"
db1.commit()
##########################################Mac Identifier##################################################
Mac_Addr = [0 for i in range(client_no)]
Mac_Addr[0] = 183541260428269
Mac_Addr[1] = 165456192814892
Mac_Addr[2] = 142980269150306
Mac_Addr[3] = 90713365256688	
Mac_Addr[4] = 161292448949420
Mac_Addr[5] = 7624882274405
Mac_Addr[6] = 94629590238303
Mac_Addr[7] = 253119606053972
Mac_Addr[8] = 122011585368124	
Mac_Addr[9] = 135182180468108
Mac_Addr[10] = 24967744637051
def TagID(mac_address):
	for i in range(len(Mac_Addr)):
		if mac_address == Mac_Addr[i]:return i
###########################################Client Thread##################################################			
def ClientThread(conn,db,addr):
    x = 0
    y = 0
    ID = ""
    conn.settimeout(30)
    while True:			
		try:							
			data = conn.recv(1024)
			data = data.split(',')
			ID = TagID(int(data[0]))
			data[0] = ID
			data[3] = datetime.datetime.now()
			sql = (int(data[0]),int(data[1]),int(data[2]),data[3])
			db.execute('''INSERT INTO DATA VALUES(?,?,?,?)''',sql)
			db.commit()
			db1.execute('''INSERT INTO DATA VALUES(?,?,?,?)''',sql)
			db1.commit()
			x = 0 	
			y = 0	
		except Exception as msg:
			err = msg.message
			if err == "invalid literal for int() with base 10: ''":
				y += 1
				if y == 20:
					print "Disconnected (Invalid Literal) after " + str(y) + " trys from node " + str(ID) 
					conn.close()
					ClientThread.running = False
					break
			if err == "timed out":
				x += 1
				if x == 20:
					print "Disconnected (Timed out) after " + str(x) + " trys from node " + str(ID) 
					conn.close()
					ClientThread.running = False
					break			
			pass	
############################################Relay Thread##################################################			 
def RelayFeedThread(f,g,relaycontroller): 
    while True:
		try:
			os.system("cp /home/wcl-lab/input /home/wcl-lab/input1") 
			sleep(3)
			f1 = open("/home/wcl-lab/input1", "r+")
			x = f1.read()
			f1.close()	
			if x:
				if int(x) == 1 and f == True:
					relaycontroller.array_on(1)
					print "Receiving from relay board: ON"
					f = False
					g = True
				if int(x) == 0 and g == True:
					relaycontroller.array_off(1)
					print "Receiving from relay board: OFF"
					g = False	
					f = True
		except Exception as msg:
			err = msg.message
			print err 
			print msg
			sleep(2)
			if str(msg) == "[Errno 19] No such device (it may have been disconnected)":
				relaycontroller = simpleusbrelay(idVendor, idProduct)
			print "Enter Exception"							
			pass								
################################################Main######################################################
while True:
	if relay_flag == 1:
		print "Relay thread started..."
		start_new_thread(RelayFeedThread ,(True,True,relaycontroller))	
		relay_flag = 0
	conn, addr = s.accept()
	print 'Connected with ' + addr[0] + ':' + str(addr[1])
	start_new_thread(ClientThread ,(conn,db,addr))

	

