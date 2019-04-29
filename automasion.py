#!/usr/bin/env python
import os
import sqlite3
import time
import datetime

f = True 
g = True
while True:
	try:		
		if datetime.datetime.now().hour == 22 and f:
			f = False
			os.system("rm /var/www/html/project/database/Data-set.db")
			os.system("cp /home/wcl-lab/server/Data-set.db /var/www/html/project/database/Data-set.db") 
			conn = sqlite3.connect('/var/www/html/project/database/Data-set.db')
			print "Opened Database(Master) Successfully.";
			conn.execute("DELETE FROM DATA WHERE last_valid_data <= date('now','-15 day')")
			conn.commit()
			print "Deleting Unuseful Data(Master) Successfully.";
			# cursor = conn.execute("SELECT id, temperature, humidity, last_valid_data from DATA")
			# for row in cursor:
			   # print "ID: ", row[0] 
			   # print "Temperature: ", row[1]
			   # print "Humidity: ", row[2]
			   # print "Last Valid Data: ", row[3], "\n"
			print "Operation(Master) Done Successfully.";
			conn.close()	
		if datetime.datetime.now().hour == 22 and g:
			g = False
			db1 = sqlite3.connect('/var/www/html/project/database/Data-set-Real-Time.db')
			print "Opened Database(Real-Time) Successfully.";
			cursor = db1.execute("DELETE from DATA")
			db1.commit()
			print "Deleting Table(Real-Time) Successfully.";
			db1.close()
			print "Operation(Real-Time) Done Successfully.";
		else:
			g = True
			f = True
			time.sleep(1900)			
	except:
		f = True
		g = True
		print "Enter Exception"
		pass
		time.sleep(3)
