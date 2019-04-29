#!/usr/bin/env python
import os
import sys
import errno
import sqlite3
import datetime
import matlab.engine
from thread import *
from time import sleep
###############################################################################################################
T_avg = 0
FB_avg = 0
client_no = 11																		# Number of clients
Ts = 1800 - 3																		# MPC Sampling time
lim = 48																			# Prediction horizon
###############################################################################################################
def SavingMovments():		
	f1 = True
	while f1:
		try:
			f1 = False 
			f = open("/home/wcl-lab/measured_output", "r+")
			MO = f.read()
			f.close()
			f = open("/home/wcl-lab/setpoint", "r+")
			SP = f.read()
			f.close()
			f = open("/home/wcl-lab/input1", "r+")
			MV = f.read()
			f.close()			
			conn = sqlite3.connect('/home/wcl-lab/server/MPC-Movments.db')
			sql = (MO,SP,MV,datetime.datetime.now() - datetime.timedelta(seconds = Ts))
			conn.execute('''INSERT INTO AIRWASHER VALUES(?,?,?,?)''',sql)
			conn.commit()
			print "Saved Movments Successfully to Database(MPC-Movments)";
			conn.close()
		except:
			f1 = True
			print "Failed to Write(MPC-Movments)..."
			sleep(2)
			conn = sqlite3.connect('/home/wcl-lab/server/MPC-Movments.db')
			pass
###############################################################################################################
def DefaultSetpoint():
	f = open('/home/wcl-lab/default-setpoint',"r+")
	a = f.readlines()
	for i in range(12):
		b = a[i].split('=')
		clock = b[0].split('-')
		if (int(clock[0]) <= datetime.datetime.now().hour and datetime.datetime.now().hour < int(clock[1])):
			b = b[1].split(' ')
			return float(b[1])
###############################################################################################################
def InputLogging(p):
	ON_Time = 0
	OFF_Time = 0
	for i in range(len(p)-1):
		if str(p[i]) == str([1.0]):ON_Time += 1
	OFF_Time = 48 - ON_Time
	print "ON Time = " + str(ON_Time * (0.5))
	print "OFF Time = " + str(OFF_Time * (0.5))
	conn = sqlite3.connect('/var/www/html/project/database/Energy-Consumption.db')
	print "Opened Database(Energy-Consumption) Successfully";
	sql = (ON_Time,OFF_Time,datetime.datetime.now())
	conn.execute('''INSERT INTO AIRWASHER VALUES(?,?,?)''',sql)
	conn.commit()
	print "Saved Commands Successfully to Database(Energy-Consumption)";
	conn.close()
###############################################################################################################
def ReadMostUpdatedFeedback():
	start = str(datetime.datetime.now() - datetime.timedelta(seconds = Ts*2))
	conn = sqlite3.connect('/var/www/html/project/database/Feedback-Data.db')
	A = 19																				#Start time = 19
	B = 6																				#Stop time = 6
	temp = 0
	hum = 0
	number_temp = 0
	number_hum = 0
	user_no = 23
	g = True
	while g:
		try:
			for i in range(user_no):	
				ID = i
				sql = str("SELECT TEMPFEEDBACK,HUMFEEDBACK,DATE from feedback WHERE id="+str(ID)+" ORDER BY DATE DESC LIMIT 1")
				cursor = conn.execute(sql)	
				for row in cursor:
					if row[2] > start:
						if row[0] != "":
							temp = row[0] + temp
							number_temp += 1	
						if row[1] != "":
							hum = row[1] + hum
							number_hum += 1
			g = False	
		except:
			g = True
			print "Failed to Fetch..."
			sleep(2)
			conn = sqlite3.connect('/var/www/html/project/database/Feedback-Data.db')
			pass
	T_now = datetime.datetime.now().hour		
	if temp == 0 or A <= T_now or T_now < B:
		FB_avg = 0
	else:
		FB_avg = float(temp)/number_temp
	conn.close()
	print "New Data(Feedback) Received"
	return FB_avg
###############################################################################################################
def ReadMostUpdatedValue():
	cmd = str("cp /var/www/html/project/database/Data-set-Real-Time.db /home/wcl-lab/server/MostUpdatedValue.db")
	os.system(cmd) 
	conn = sqlite3.connect('/home/wcl-lab/server/MostUpdatedValue.db')
	temp = 0
	hum = 0
	number = 0
	f = True
	while f:
		try:
			for i in range(client_no):		
				ID = i	
				sql=str("SELECT temperature,humidity from DATA WHERE id="+str(ID)+" ORDER BY last_valid_data DESC LIMIT 1")
				cursor = conn.execute(sql)
				for row in cursor:
					temp = row[0] + temp
					#hum = row[1] + hum
					number += 1		
			f = False	
		except:
			f = True
			print "Failed to Fetch(Measured Output)..."
			sleep(2)
			os.system(cmd) 
			conn = sqlite3.connect('/home/wcl-lab/server/MostUpdatedValue.db')
			pass
	conn.close()							
	T_avg = float(temp)/(number)		
	#H_avg = float(hum)/(number)	
	print "New Data(Measured Output) Received"
	return T_avg
###############################################################################################################
def FeedThread(Ts,lim):
	cnt = 0
	while cnt != lim:
		try:
			sleep(Ts)
			SavingMovments()
			if cnt != 48:
				T_avg = ReadMostUpdatedValue()
				f = open('/home/wcl-lab/measured_output','w+')
				f.write(str(T_avg))
				f.close()
				print "Sent Measured Output to MatLab = " + str(T_avg)
				FB_avg = ReadMostUpdatedFeedback()
				if FB_avg != 0:
					f2 = open('/home/wcl-lab/setpoint','w+')
					f2.write(str(FB_avg))
					f2.close()
					print "Sent Setpoint(Feedback) to MatLab = " + str(FB_avg)
				if FB_avg == 0:
					FB_avg = DefaultSetpoint()
					f2 = open('/home/wcl-lab/setpoint','w+')
					f2.write(str(FB_avg))
					f2.close()
					print "Sent Setpoint(Default) to MatLab = " + str(FB_avg)					
			f1 = open('/home/wcl-lab/input','r+')
			u = f1.read()
			print "Movment Received = " + str(u)
			cnt += 1
			#print cnt
			f1.close()
		except: 
			print "Cant Read/Write from/to Shared Files!"
			pass
###############################################################################################################		
end = True
while end:
	try:
	####################################Sending Initial Data to MatLab#########################################	
		l = 13
		end = False
		f = open('/home/wcl-lab/measured_output','w+')
		y0 = ReadMostUpdatedValue()
		f.write(str(y0))	
		f.close()
		print "Sent Initial Temperature(y0) to MatLab = " + str(y0)
		FB_avg = ReadMostUpdatedFeedback()
		if FB_avg != 0:
			f2 = open('/home/wcl-lab/setpoint','w+')
			f2.write(str(FB_avg))
			f2.close()
			print "Sent Initial Setpoint(Feedback) to MatLab = " + str(FB_avg)
		else:
			FB_avg = DefaultSetpoint()
			f2 = open('/home/wcl-lab/setpoint','w+')
			f2.write(str(FB_avg))
			f2.close()
			print "Sent Initial Setpoint(Default) to MatLab = " + str(FB_avg)		
	##########################################Starting Feed Thread##############################################	
		start_new_thread(FeedThread ,(Ts,lim))
	#########################################Calling MPC from MatLab############################################	
		n = str(matlab.engine.find_matlab())
		n = n[2:l]
		print "Connecting to " + n
		eng = matlab.engine.connect_matlab(n)
		p = eng.transferfunc_winter(y0)	
		#print p
		f1 = open('/home/wcl-lab/input','r+')
		u = f1.read()
		print "Last Movment Received = " + str(u)
		f1.close()
	############################################Logging MPC Movments############################################	
		try:
			f2 = open('/home/wcl-lab/input-log','a')
			f2.write("\n")
			f2.write(str(p))
			f2.write("\n")
			f2.close()			
			InputLogging(p)		
		except: 
			print "Cant Save Commands to Database..."
			continue
	############################################Preparing to Restart############################################		
		if p:
			print "Preparing for Start... "
			end = True
			eng.quit()
			FeedThread.running = False
			sleep(10)		
	except:
		print "Something Wrong..."
		sleep(10)
		l = 14
		end = True
		pass
