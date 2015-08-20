#!/usr/bin/env python


from irpos import *
import rospy
import math
import sys
import threading
from Tkinter import Tk
from tkFileDialog import askopenfilename
from std_msgs.msg import Float32MultiArray
import std_msgs.msg
import model
import cv2
import numpy

DataLock = threading.Lock()
TableLock = threading.Lock()
NewLock = threading.Lock()
global move_x
move_x=0
global move_y
move_y=0
global rads
rads=0
global first_time
first_time=0
global BlockPos
global Board
global NewBoard
global Overboard
global Reds
global Greens
global Blues
global NewReds
global NewGreens
global NewBlues
global ReqBoard
#For init
ReqBoard=False
NewBoard=[]
Overboard=-1
BlockPos=[]
Board=[]
Reds=[]
Greens=[]
Blues=[]
	
	
def clear_new():
	global NewReds
	global NewGreens
	global NewBlues
	NewLock.acquire()
	NewReds = False
	NewGreens = False
	NewBlues = False
	NewLock.release()
	
def central_pos(x):
	#print x
	return (x[0]+x[1]+x[2]+x[3])/len(x)
	
def rotation(xy):
	try:
		if xy[1]>xy[0]:
			temp=xy[1]
			xy[1]=xy[0]
			xy[0]=temp
			temp=xy[3]
			xy[3]=xy[2]
			xy[2]=temp
		if xy[3]>xy[2]:
			#print 'obrot w prawo'
			alpha=-math.fabs(xy[1]-xy[0])/math.fabs(xy[3]-xy[2]) #dx/dy
			if math.atan(alpha)<-1:
				#print "PRZEKROCZONE w prawo"
				return math.atan(alpha)+3.1415
		else:
			#print 'obrot w lewo'
			alpha=math.fabs(xy[1]-xy[0])/math.fabs(xy[3]-xy[2]) #dx/dy
		return math.atan(alpha)
	except:
		#print "Divided by zero, vertical line, assuming zero"
		return 0
	
def choose_block(color, siz, mod='CLOSEST'):
	#print " RED BLUES GREENS"
	#print Reds
	#print Blues
	#print Greens
	#print "Color"
	#print color
	#print "Size"
	#print siz
	clear_new()
	chosen = []
	deltamax = 90000.0
	deltamin = 0.0
	founded=[]
	for error_rate in range(0,10):
		if error_rate > 0:
			print "NO NEEDED BRICK FOUND FOR " + str(error_rate) + " CYCLES. WAITING."
			rospy.sleep(1)
		if color == "b":
			TableLock.acquire()
			for i in Blues:
				if i[0]==float(siz):
					print "Chosen bricks:"
					print i
					chosen.append(i)
			TableLock.release()
			for i in chosen:
				if mod=='CLOSEST':
					#print "CLOSEST mod"
					if deltamax>(math.fabs(i[1])+math.fabs(i[2])):
						deltamax=math.fabs(i[1])+math.fabs(i[2])
						founded=i
				elif mod=='FURTHEST':
					#print "FURTHEST mod"
					if deltamin<(math.fabs(i[1])+math.fabs(i[2])):
						deltamin=math.fabs(i[1])+math.fabs(i[2])
						founded=i
			#print "Chosen brick:"
			#print founded
			if founded==[]:
				continue
			if siz == "2" and math.fabs(founded[3])>(math.pi/4):
				#print "Rotation for 2 over pi/4, new"
				if founded[3]<0:
					founded[3]=founded[3]+(math.pi/2)
				else:
					founded[3]=founded[3]-(math.pi/2)
				print founded[3]
			#print "Rotation for 2 " + str(founded[3])
			return founded
		elif color== "r":
			TableLock.acquire()
			for i in Reds:
				if i[0]==float(siz):
					#print "Chosen bricks:"
					#print i
					chosen.append(i)
			TableLock.release()
			for i in chosen:
				if mod=='CLOSEST':
					#print "CLOSEST mod"
					if deltamax>(math.fabs(i[1])+math.fabs(i[2])):
						deltamax=math.fabs(i[1])+math.fabs(i[2])
						founded=i
				elif mod=='FURTHEST':
					#print "FURTHEST mod"
					if deltamin<(math.fabs(i[1])+math.fabs(i[2])):
						deltamin=math.fabs(i[1])+math.fabs(i[2])
						founded=i
			#print "Chosen brick:"
			#print founded
			if founded==[]:
				continue
			if siz == "2" and math.fabs(founded[3])>(math.pi/4):
				#print "Rotation for 2 over pi/4, new"
				if founded[3]<0:
					founded[3]=founded[3]+(math.pi/2)
				else:
					founded[3]=founded[3]-(math.pi/2)
				print founded[3]
			#print "Rotation for 2 " + str(founded[3])
			return founded
		elif color== "g":
			TableLock.acquire()
			for i in Greens:
				if i[0]==float(siz):
					#print "Chosen bricks:"
					#print i
					chosen.append(i)
			TableLock.release()
			for i in chosen:
				if mod=='CLOSEST':
					#print "CLOSEST mod"
					if deltamax>(math.fabs(i[1])+math.fabs(i[2])):
						deltamax=math.fabs(i[1])+math.fabs(i[2])
						founded=i
						#print "founded new:"
						#print i
				elif mod=='FURTHEST':
					#print "FURTHEST mod"
					if deltamin<(math.fabs(i[1])+math.fabs(i[2])):
						deltamin=math.fabs(i[1])+math.fabs(i[2])
						founded=i
						#print "founded new:"
						#print i
			#print "Chosen brick:"
			#print founded
			if founded==[]:
				continue
			if siz == "2" and math.fabs(founded[3])>(math.pi/4):
				#print "Rotation for 2 over pi/4, new"
				if founded[3]<0:
					founded[3]=founded[3]+(math.pi/2)
				else:
					founded[3]=founded[3]-(math.pi/2)
				print founded[3]
			#print "Rotation for 2 " + str(founded[3])
			return founded
		TableLock.release()
	return 'ERROR'
	
	
def info(y,x,scale_modifier=1):
	dist_min = math.sqrt( (y[0] - y[1])**2 + (x[0] - x[1])**2 )
	dist_min_pos = [y[0],y[1],x[0],x[1]]
	dist_max = math.sqrt( (y[0] - y[1])**2 + (x[0] - x[1])**2 )
	dist_max_pos = [y[0],y[1],x[0],x[1]]
	for i in range(1,3):
		dist = math.sqrt( (y[i] - y[i+1])**2 + (x[i] - x[i+1])**2 )
		if dist_min > dist:
			dist_min=dist
			dist_min_pos = [y[i],y[i+1],x[i],x[i+1]]
		if dist_max < dist:
			dist_max = dist
			dist_max_pos = [y[i],y[i+1],x[i],x[i+1]]
	dist = math.sqrt( (y[3] - y[0])**2 + (x[3] - x[0])**2 )
	if dist_min > dist:
		dist_min=dist
		dist_min_pos = [y[3],y[0],x[3],x[i+1]]
	if dist_max < dist:
		dist_max = dist
		dist_max_pos = [y[3],y[0],x[3],x[0]]
	size=round(dist_max/dist_min)
	
	rot=rotation(dist_max_pos)
	if scale_modifier==4:
		if rot > rot-(math.pi/2) and rot-(math.pi/2)>-1:
			rot = rot-(math.pi/2)
			
	if scale_modifier==1 and rot<math.pi/4:
		#print "ELSE"
		point3 = numpy.array([[0.0159*size,-0.0159,0.01175], 
					[-0.0159*size,-0.0159,0.01175], 
					[-0.0159*size,0.0159,0.01175], 
					[0.0159*size,0.0159,0.01175]], numpy.float32) 
	elif scale_modifier==1:
		#print "ELSE"
		point3 = numpy.array([[0.0159,-0.0159*size,0.01175], 
					[-0.0159,-0.0159*size,0.01175], 
					[-0.0159,0.0159*size,0.01175], 
					[0.0159,0.0159*size,0.01175]], numpy.float32) 
	elif scale_modifier==4:
		#print "BOARD SCALE MOD"
		#print x
		#print y
		point3 = numpy.array([[0.0636,-0.0636,0.01175], 
					[-0.0636,-0.0636,0.01175], 
					[-0.0636,0.0636,0.01175], 
					[0.0636,0.0636,0.01175]], numpy.float32) 
	size=size*2
	point21 = numpy.array([[x[0],y[0]], 
                  [x[1],y[1]],
                  [x[2],y[2]],
                  [x[3],y[3]]], numpy.float32) 
	point2 = numpy.ascontiguousarray(point21[:,:2]).reshape((4,1,2))
	campoint = numpy.array([[869.608276,0.000000,638.279177], 
                  [0.000000,922.489136,512.939969], 
                  [0.000000,0.000000,1.000000]], numpy.float32) 
	
	#print "WEKTORY!"
	#listener = tf.TransformListener()	
	#j=0
	#while(j<2):
	#	try:
	#		(tftrans,tfrot) = listener.lookupTransform('/pl_6', '/p_c_optical_frame', rospy.Time(0))
	#	except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
	#		j=j+1
	#		time.sleep(0.1)
	#		if j==1:
	#			#print "exception in lookupTransform!"
	#		continue
	#	break
	#print tftrans
	#print "Rot"
	#print tfrot
	
	found, rvec, tvec = cv2.solvePnP(point3,point2,campoint,numpy.array([0.0, 0.0, 0.0, 0.0]),flags=cv2.CV_P3P)
	#tvec=array(tvec)
	tvec[0][0]=float(-tvec[0][0])#-tftrans[1]
	tvec[1][0]=float(tvec[1][0])-0.05#-tftrans[0]
	
	return [size,tvec[0][0],tvec[1][0],rot]

def info2(x,y, scale_modifier=1):
	test = info2(x,y, scale_modifier)
	dist_min = math.sqrt( (x[0] - x[1])**2 + (y[0] - y[1])**2 )
	dist_min_pos = [x[0],x[1],y[0],y[1]]
	dist_max = math.sqrt( (x[0] - x[1])**2 + (y[0] - y[1])**2 )
	dist_max_pos = [x[0],x[1],y[0],y[1]]
	for i in range(1,3):
		dist = math.sqrt( (x[i] - x[i+1])**2 + (y[i] - y[i+1])**2 )
		if dist_min > dist:
			dist_min=dist
			dist_min_pos = [x[i],x[i+1],y[i],y[i+1]]
		if dist_max < dist:
			dist_max = dist
			dist_max_pos = [x[i],x[i+1],y[i],y[i+1]]
	dist = math.sqrt( (x[3] - x[0])**2 + (y[3] - y[0])**2 )
	if dist_min > dist:
		dist_min=dist
		dist_min_pos = [x[3],x[0],y[3],y[i+1]]
	if dist_max < dist:
		dist_max = dist
		dist_max_pos = [x[3],x[0],y[3],y[0]]
	#size, dx,dy
	move_y=-((647-central_pos(x))*3.1*scale_modifier)/(dist_min*100)#650 643
	move_x=((632-central_pos(y))*3.1*scale_modifier)/(dist_min*100)#637
	#print move_x
	#print move_y
	size=round(dist_max/dist_min)*2
	rot=rotation(dist_max_pos)
	if scale_modifier==4:
		#print "ROTATION FOR BOARD HERE"
		#print rot
		if rot > rot-(math.pi/2) and rot-(math.pi/2)>-1:
			#print "ROTATION FOR BOARD REACHED LIMIT. CHANGING FROM" + str(math.degrees(rot)) + " TO " + str(math.degrees(rot-(math.pi/2)))
			rot = rot-(math.pi/2)#1.57
	print "Delta: "
	print test[0]-size
	print test[1]-move_x
	print test[2]-move_y
	print test[3]-rot
	return [size,move_x,move_y,rot]
	
def rearrange(data):
	#print("REARRANGE")
	#print(data)
	
	if data==():
		return "NO DATA RECEIVED IN PACKAGE"
	if data[0] == 0:
		global Board
		global ReqBoard
		if Board==[]:
			print "BOARD DATA HERE"
			print data
			Board = info(data[1:5],data[5:9],4)
		elif ReqBoard:
			global NewBoard
			TableLock.acquire()
			NewBoard = info(data[1:5],data[5:9],4)
			TableLock.release()
		return "Received Board data"
	global Reds
	global Greens
	global Blues
	rows=len(data)
	table=[]
	i=0
	while i<rows:
		table.append(info(data[i+1:i+5],data[i+5:i+9]))
		i=i+9;
	#print(table)
	
	if data[0] == 1:
		global NewReds
		NewLock.acquire()
		NewReds=True
		NewLock.release()
		TableLock.acquire()
		Reds=table
		TableLock.release()
		publisher.publish("Reds;"+str(table))
		return "Received Reds Data"
	elif data[0] == 2:
		global NewGreens
		NewLock.acquire()
		NewGreens=True
		NewLock.release()
		TableLock.acquire()
		Greens=table
		TableLock.release()
		publisher.publish("Greens;"+str(table))
		return "Received Greens Data"
	elif data[0] == 3:
		global NewBlues
		NewLock.acquire()
		NewBlues=True
		NewLock.release()
		TableLock.acquire()
		Blues=table
		TableLock.release()
		publisher.publish("Blues;"+str(table))
		return "Received Blues Data"

def scale_rotation(y,x):
	global move_x
	global move_y
	global rads
	global first_time
	dist_min = math.sqrt( (x[0] - x[1])**2 + (y[0] - y[1])**2 )
	dist_min_pos = [x[0],x[1],y[0],y[1]]
	dist_max = math.sqrt( (x[0] - x[1])**2 + (y[0] - y[1])**2 )
	dist_max_pos = [x[0],x[1],y[0],y[1]]
	for i in range(1,3):
		dist = math.sqrt( (x[i] - x[i+1])**2 + (y[i] - y[i+1])**2 )
		if dist_min > dist:
			dist_min=dist
			dist_min_pos = [x[i],x[i+1],y[i],y[i+1]]
		if dist_max < dist:
			dist_max = dist
			dist_max_pos = [x[i],x[i+1],y[i],y[i+1]]
	move_x=((650-central_pos(x))*3.1)/dist_min #655
	move_y=((650-central_pos(y))*3.1)/dist_min #637 650
	move_y=-move_y/100
	move_x=move_x/100
	rads = rotation(dist_max_pos)
			
def callback(data):
	global BlockPos
	# DATA: num,y1,y2,y3,y4,x1,x2,x3,x4
	#rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
	#print(rearrange(data.data))
	rearrange(data.data)
	DataLock.acquire()
	if BlockPos != []:
		BlockPos=[]
	for elem in data.data:
		try:
			BlockPos.append(elem)
		except:
			print "Error reading data!"
			BlockPos=[]
			break
	DataLock.release()
	
	
def main():
	autostop=0
	rospy.sleep(1)
	publisher.publish("Ready")
	rospy.sleep(6)
	publisher.publish("Unready")
	rospy.sleep(1)
	while 1:
		autostop=0
		while Overboard==-1:
			move_overboard()
			autostop=autostop+1
			rospy.sleep(0.01)
			if autostop >= 1000:
				print "NO BOARD. STOP"
				return
		global BlockPos
		#print "Check position"	
		#print irpos.get_tfg_joint_position()
		
		#print "Trying move_operation"
		DataLock.acquire()
		if BlockPos != []:
			DataLock.release()
			print "BEGINNING MOVE OP"
			try:
				print move_operation()
			except:
				return
			print "ENDED MOVE OP"
			return
			autostop=0
		else:
			DataLock.release()
			autostop+=1
			rospy.sleep(0.01)
			if autostop>1000:
				print "CONNECTION TIMEOUT. STOP"
				break

	
def move_over(move_x, move_y, rads):
	print "Move over time " + str(math.fabs(move_x)+math.fabs(move_y)*10+1.0)
	irpos.move_rel_to_cartesian_pose((math.fabs(move_x)+math.fabs(move_y))*10+1.0, Pose(Point(move_x, move_y, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
	rotate(rads)
	return

def rotate(rads):
    myjoint = irpos.get_joint_position()
    lst = list(myjoint)
    lst[5] = lst[5]-rads
    myjoint = tuple(lst)
    irpos.move_to_joint_position(myjoint, float(math.fabs(rads*(16/math.pi)))+1.0)
    return
    	
def grab_brick():
	irpos.tfg_to_joint_position(0.09, 5.0)
	irpos.move_rel_to_cartesian_pose_with_contact(9.0, Pose(Point(0, 0, 0.3), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(12.0,12.0,12.0),Vector3(0.0,0.0,0.0)))
	irpos.move_rel_to_cartesian_pose(1.0, Pose(Point(0, 0, -0.005), Quaternion(0.0, 0.0, 0.0, 1.0)))
	irpos.tfg_to_joint_position(0.07, 5.0)
	publisher.publish("Grabbing")
	irpos.move_rel_to_cartesian_pose(1.0, Pose(Point(0, 0, -0.05), Quaternion(0.0, 0.0, 0.0, 1.0)))
	#irpos.move_to_joint_position([ 7.412760409739285e-06, -1.764427006069524, 0.0006186793623569331, 0.1930235079212923, 4.7123619308455735, 1.5707923033898181], 10.0)
	service_position()
	
def put_brick(offset=0, heigth=0):
	toright_offset=0.0#01
	print "Offset: "+str(offset)+ " equals " + str(offset*0.015)#0.016
	move_overboard()
	irpos.move_rel_to_cartesian_pose(math.fabs(offset)*0.5+1.0, Pose(Point(offset*0.015+0.03, toright_offset, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
	#heigth=2.3 cm/2
	#irpos.move_rel_to_cartesian_pose(2.0, Pose(Point(0.03, toright_offset, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
	irpos.move_rel_to_cartesian_pose(4.0, Pose(Point(0, 0, 0.195-(heigth*0.020)-0.005), Quaternion(0.0, 0.0, 0.0, 1.0)))#, Wrench(Vector3(8.0,8.0,8.0),Vector3(0.0,0.0,0.0)))
	irpos.move_rel_to_cartesian_pose(1.0, Pose(Point(-0.027, 0, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))#, Wrench(Vector3(8.0,8.0,8.0),Vector3(0.0,0.0,0.0)))
	irpos.move_rel_to_cartesian_pose(1.0, Pose(Point(0, 0, 0.005), Quaternion(0.0, 0.0, 0.0, 1.0)))#, Wrench(Vector3(8.0,8.0,8.0),Vector3(0.0,0.0,0.0)))
	
	
	
	
	print "Open"
	irpos.tfg_to_joint_position(0.09, 5.0)
	publisher.publish("Putting")
	
	irpos.move_rel_to_cartesian_pose(1.5, Pose(Point(0, -toright_offset, -0.025), Quaternion(0.0, 0.0, 0.0, 1.0)))#, Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
	
def push_brick(mod="NONE"):
	#mod CROSS NONE UP
	force=10.0 #force to push brick
	irpos.tfg_to_joint_position(0.055, 5.0)
	irpos.move_rel_to_cartesian_pose_with_contact(4.0, Pose(Point(0, 0, 0.08), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(force,force,force),Vector3(0.0,0.0,0.0)))
	rect_size=0.005
	#bring effector up
	irpos.move_rel_to_cartesian_pose(1.0, Pose(Point(0, 0, -0.0005), Quaternion(0.0, 0.0, 0.0, 1.0)))
	
	
	#dol lewo
	irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(-rect_size, -rect_size/2, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
	#dol prawo
	irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(-rect_size, rect_size/2, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
	#slight push
	irpos.move_rel_to_cartesian_pose(1.0, Pose(Point(0, 0, 0.002), Quaternion(0.0, 0.0, 0.0, 1.0)))
	irpos.move_rel_to_cartesian_pose(1.0, Pose(Point(0, 0, -0.002), Quaternion(0.0, 0.0, 0.0, 1.0)))
	#gora prawo
	irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(rect_size, rect_size/2, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
	#gora lewo
	irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(rect_size, -rect_size/2, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
	
	if mod=="CROSS":
		#dol
		irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(-rect_size, 0, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
		#2gora
		irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(rect_size*2, 0, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
		#dol
		irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(-rect_size, 0, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
		#lewo
		irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(0, -rect_size/2, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
		#2prawo
		irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(0, rect_size, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
		#lewo
		irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(0, -rect_size/2, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
	if mod=="UP":
		#2gora
		irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(rect_size, 0, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
		#dol
		irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(-rect_size*2, 0, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
		#dol
		irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(rect_size, 0, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
		
		
		
	
		
	#push
	irpos.move_rel_to_cartesian_pose_with_contact(7.0, Pose(Point(0, 0, 0.08), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(11.0,11.0,11.0),Vector3(0.0,0.0,0.0)))
	
	#go up
	irpos.move_rel_to_cartesian_pose_with_contact(2.0, Pose(Point(0, 0, -0.05), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
	
	#push
	irpos.move_rel_to_cartesian_pose_with_contact(7.0, Pose(Point(0, 0, 0.08), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(13.0,13.0,13.0),Vector3(0.0,0.0,0.0)))
		
def service_position(effector=0):
	#print irpos.get_joint_position()
	if not effector==1 and not effector==2:
		irpos.move_to_joint_position([ 7.412760409739285e-06, -1.764427006069524, 0.0006186793623569331,  0.15, 4.7123619308455735, 1.48], 3.0)
		#irpos.move_rel_to_cartesian_pose_with_contact(5.0, Pose(Point(0, 0, 0.035), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
	
	else:
		print "Move to service position."
	if effector==2:
		irpos.tfg_to_joint_position(0.07, 5.0)
		
	elif  effector==1:
		irpos.move_to_joint_position([ 7.412760409739285e-06, -1.764427006069524, 0.0006186793623569331,  0.15, 4.7123619308455735, 1.48], 10.0)
		irpos.tfg_to_joint_position(0.09, 5.0)
		
	rospy.sleep(2)
	
def move_overboard():
	global Board
	global NewBoard
	global Overboard
	if Overboard==-1:
		if Board==[]:
			#print("No board in sight!")
			return -1
		else:
			print "BOARD DATA HERE:"
			print Board
			move_over(Board[1], Board[2], Board[3])
			print "Publishing 1!"
			publisher.publish("Board;rotation;"+str(Board[3]))
			print "Published 1!"
			rospy.sleep(5)
			for i in range(0,10):
				global ReqBoard
				ReqBoard = True
				TableLock.acquire()
				if NewBoard != []:
					move_over(NewBoard[1], NewBoard[2], NewBoard[3])
					TableLock.release()
					break
				TableLock.release()
				rospy.sleep(1)
				
			
			irpos.move_rel_to_cartesian_pose_with_contact(10.0, Pose(Point(0, 0, 0.3), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(12.0,12.0,12.0),Vector3(0.0,0.0,0.0)))
			rospy.sleep(1)
			#irpos.move_rel_to_cartesian_pose_with_contact(20.0, Pose(Point(0, 0, -0.2), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(6.0,6.0,6.0),Vector3(0.0,0.0,0.0)))
	
			irpos.move_rel_to_cartesian_pose(4.0, Pose(Point(0, 0, -0.2), Quaternion(0.0, 0.0, 0.0, 1.0)))
			#print "Publishing 2!"
			publisher.publish("Board;position")
			#print "Published 2!"
	
			Overboard=irpos.get_joint_position()
			lst = list(Overboard)
			lst.append(10.0)
			Overboard = tuple(lst)
			return 0
	else:
		print "MOVING OVERBOARD"
		irpos.move_to_joint_position(Overboard, 2)
		return 1
    
def move_operation(): 
	global Reds
	global Greens
	global Blues  
	try:
		schema = model.open_schema()
	except:
		raise Exception('Error reading file!')
	print schema
	level=0
	service_position()
	rospy.sleep(3)
	for i1 in schema:
		dist=-3
		for i2 in i1:
			if i2[1] == '.':
				dist=dist+int(i2[0])
				#print "dots dist = " + str(dist)
				continue
			dist=dist+(int(i2[0])/2)-1
			#print "afterdots dist = " + str(dist)
			print "taking"
			print dist
			print level
			result = take_operation(i2[1],i2[0],dist,level)
			if result != "Done.":
				print result
				return
			print "taking ended"
			
			dist=dist+(int(i2[0])/2)+1
			#print "afterall dist = " + str(dist)
		level=level+1
	
def take_operation(color, siz, offset=0, heigth=0, correction_mod=1):#move_x, move_y, rads, 
	global NewReds
	global NewGreens
	global NewBlues
	new_brick = choose_block(color,siz, 'FURTHEST')
	print "New brick to take:" + str(new_brick)
	if new_brick == 'ERROR':
		print "ERROR"
		return 'No brick found'
	#MOVE OVER
	move_x=new_brick[1]
	move_y=new_brick[2]
	rads=new_brick[3]
	#END MOVE OVER
	move_over(move_x, move_y, rads)
	#CORRECT
	for i in range(0,correction_mod):
		rospy.sleep(3)
		clear_new()
		error_count=20
		for j in range(1,error_count):
			NewLock.acquire()
			if color=='r' and NewReds==True:
				NewLock.release()
				break
			elif color=='g' and NewGreens==True:
				NewLock.release()
				break
			elif color=='b' and NewBlues==True:
				NewLock.release()
				break
			print "No new data to correct after "+str(j)+" tries. Retrying in 1 second."
			print "Requested color " + str(color)
			print "RGB state " + str(NewReds)+" "+ str(NewGreens)+" "+ str(NewBlues)
			NewLock.release()
			rospy.sleep(1)
			if j==error_count-1:
				return 'Brick lost during correction.'
		new_brick = choose_block(color,siz, 'CLOSEST')
		if new_brick == 'ERROR':
			print "ERROR"
			return 'No brick found'
		move_x=new_brick[1]
		move_y=new_brick[2]
		if math.fabs(new_brick[3])>0.08:
			rads=0
		else:
			rads=new_brick[3]
	
		move_over(move_x, move_y, rads)
		grab_brick()
	#END CORRECT
	#rospy.sleep(2)
	#Bring back the block
	put_brick(offset, heigth)
	#push
	push_brick()
	#return to service position
	service_position()
	#rospy.sleep(2)
	
	print "PLACING " + str(color) + str(siz) + " ENDED"
	return "Done."

if __name__ == '__main__':
	irpos = IRPOS("thIRpOS", "Irp6p", 6, 'irp6p_manager') #z csn
	service_position(1)
	#irpos.move_rel_to_cartesian_pose_with_contact(5.0, Pose(Point(0, 0, 0.035), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
	rospy.Subscriber("float32MultiArray", Float32MultiArray, callback, None, 1)
	publisher = rospy.Publisher('rviz_brick_info', String)
	main()
	publisher.publish("End")
	service_position(2)

