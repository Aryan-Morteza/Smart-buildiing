#!/usr/bin/python
import os
import sqlite3
import sys
import errno
import datetime
import time
import array
from collections import Counter
#############################################################################################################################
T_avg = 0
client_no = 11
Last_temp = [0 for i in range(client_no)]
cmd = str("cp /var/www/html/project/database/Data-set-Real-Time.db /home/wcl-lab/server/Live-monitoring.db")
#############################################################################################################################
def ReadMostUpdatedValue():
	os.system(cmd) 
	conn = sqlite3.connect('Live-monitoring.db')
	print "New data received"
	temp = 0
	hum = 0
	number = 0
	f = True
	while f:
		try:
			for i in range(client_no):		
				ID = i	
				sql=str("SELECT temperature,humidity,last_valid_data from DATA WHERE id=" + str(ID) + " ORDER BY last_valid_data DESC LIMIT 1")
				cursor = conn.execute(sql)
				for row in cursor:
					#print row[2]
					temp = row[0] + temp
					hum = row[1] + hum
					#print temp
					number += 1		
				f = False	
		except:
			f = True
			print "Failed to fetch..."
			time.sleep(1)
			os.system(cmd) 
			conn = sqlite3.connect('Live-monitoring.db')
			pass
	conn.close()							
	T_avg = float(temp)/(number)		
	H_avg = float(hum)/(number)		
	return T_avg,H_avg	
#############################################################################################################################	
print "Operation started" 
while True:
	try:
		T_avg,H_avg = ReadMostUpdatedValue()
		print "Average temperature: " + str(T_avg)
		print "Average humidity: " + str(H_avg)
		time.sleep(60)	
	except:
		print "e"
		pass
