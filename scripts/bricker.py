#!/usr/bin/env python


from irpos import *
import rospy
import math
import sys
import threading
from Tkinter import Tk
from tkFileDialog import askopenfilename
from std_msgs.msg import Float32MultiArray
import model

DataLock = threading.Lock()
TableLock = threading.Lock()
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
global Overboard
global Reds
global Greens
global Blues
#For init
Overboard=-1
BlockPos=[]
Board=[]
Reds=[]
Greens=[]
Blues=[]

def createPose(x, y, z, ox, oy, oz, ow):
	position = Point(x, y, z)
	quaternion = Quaternion(ox, oy, oz, ow)

	P = Pose(position, quaternion)
	return P
	
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
		print "Divided by zero, vertical line, assuming zero"
		return 0
	
def choose_block(colour, siz, mod='CLOSEST'):
	print " RED BLUES GREENS"
	print Reds
	print Blues
	print Greens
	print "Colour"
	print colour
	print "Size"
	print siz
	chosen = []
	deltamax=90000.0
	deltamin=0.0
	founded=[]
	for error_rate in range(0,10):
		if colour == "b":
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
			return founded
		elif colour== "r":
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
			return founded
		elif colour== "g":
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
			return founded
		TableLock.release()
		print "NO NEEDED BRICK FOUND FOR " + str(error_rate) + " CYCLES. WAITING."
		rospy.sleep(1)
	return 'ERROR'
	
def info(x,y, scale_modifier=1):
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
	move_y=-((652-central_pos(x))*3.1*scale_modifier)/(dist_min*100)#655
	move_x=((632-central_pos(y))*3.1*scale_modifier)/(dist_min*100)#637
	size=round(dist_max/dist_min)*2
	rot=rotation(dist_max_pos)
	if scale_modifier==4:
		print "ROTATION FOR BOARD HERE"
		print rot
		if rot > rot-1.57 and rot-1.57>-1:
			print "ROTATION FOR BOARD REACHED LIMIT. CHANGING FROM" + str(math.degrees(rot)) + " TO " + str(math.degrees(-rot+1.57))
			rot = rot-(math.pi/2)#1.57
			
	return [size,move_x,move_y,rot]
	
def rearrange(data):
	#print("REARRANGE")
	#print(data)
	
	if data==():
		return "NO DATA RECEIVED IN PACKAGE"
	if data[0] == 0:
		global Board
		if Board==[]:
			print "BOARD DATA HERE"
			print data
			Board = info(data[1:5],data[5:9],4)
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
		TableLock.acquire()
		Reds=table
		TableLock.release()
		return "Received Reds Data"
	elif data[0] == 2:
		TableLock.acquire()
		Greens=table
		TableLock.release()
		return "Received Greens Data"
	elif data[0] == 3:
		TableLock.acquire()
		Blues=table
		TableLock.release()
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
	move_x=((655-central_pos(x))*3.1)/dist_min #655
	move_y=((655-central_pos(y))*3.1)/dist_min #637 650
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
	
	
def listener():
	autostop=0
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
			move_operation()
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

	
def move_over(move_x, move_y, rads, time=15.0):
    irpos.move_rel_to_cartesian_pose_with_contact(12.0, Pose(Point(move_x, move_y, 0), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
    rotate(rads)
    return

def rotate(rads):
    myjoint = irpos.get_joint_position()
    lst = list(myjoint)
    lst[5] = lst[5]-rads
    myjoint = tuple(lst)
    irpos.move_to_joint_position(myjoint, 8.0)
    return
    
def correction(move_x, move_y, rads):
	#Move down to correct
	irpos.move_rel_to_cartesian_pose_with_contact(5.0, Pose(Point(0, 0, 0.05), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
	if move_x<0.05:# and move_x>0.0005:
		print "Correcting x"
		irpos.move_rel_to_cartesian_pose_with_contact(3.0, Pose(Point(move_x, 0, 0), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
	if move_y<0.05:# and move_y>0.0005:
		print "Correcting y"
		irpos.move_rel_to_cartesian_pose_with_contact(3.0, Pose(Point(0, move_y, 0), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
	print rads
	if math.fabs(rads)<math.radians(1) and math.fabs(rads)>math.radians(0.05):
		print "Correcting rotation"
		rotate(rads)
		
def grab_brick():
	irpos.tfg_to_joint_position(0.09, 5.0)
	irpos.move_rel_to_cartesian_pose_with_contact(20.0, Pose(Point(0, 0, 0.3), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(7.0,7.0,7.0),Vector3(0.0,0.0,0.0)))
	irpos.move_rel_to_cartesian_pose_with_contact(6.0, Pose(Point(0, 0, -0.005), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
	irpos.tfg_to_joint_position(0.073, 5.0)
	irpos.move_rel_to_cartesian_pose_with_contact(10.0, Pose(Point(0, 0, -0.2), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
	irpos.move_to_joint_position([ 7.412760409739285e-06, -1.764427006069524, 0.0006186793623569331, 0.1930235079212923, 4.7123619308455735, 1.5707923033898181], 10.0)
	
def put_brick(offset=0, heigth=0):
	print "Offset: "+str(offset)+ " equals " + str(offset*0.016)
	move_overboard()
	irpos.move_rel_to_cartesian_pose_with_contact(5.0, Pose(Point(offset*0.016, 0, 0), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(6.0,6.0,6.0),Vector3(0.0,0.0,0.0)))
	#heigth=2.3 cm/1.9
	#irpos.move_rel_to_cartesian_pose_with_contact(20.0, Pose(Point(0, 0, 0.3), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(6.0,6.0,6.0),Vector3(0.0,0.0,0.0)))
	irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(0.03, 0, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
	irpos.move_rel_to_cartesian_pose_with_contact(14.0, Pose(Point(0, 0, 0.195-(heigth*0.024)), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(6.0,6.0,6.0),Vector3(0.0,0.0,0.0)))
	irpos.move_rel_to_cartesian_pose_with_contact(3.0, Pose(Point(-0.025, 0, 0), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(6.0,6.0,6.0),Vector3(0.0,0.0,0.0)))
	irpos.move_rel_to_cartesian_pose_with_contact(3.0, Pose(Point(0, 0, 0.005), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(6.0,6.0,6.0),Vector3(0.0,0.0,0.0)))
	
	
	
	
	print "Open"
	irpos.tfg_to_joint_position(0.09, 5.0)
	
	irpos.move_rel_to_cartesian_pose_with_contact(5.0, Pose(Point(0, 0, -0.025), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
	
def push_brick(mod="CROSS"):
	#mod CROSS RECT
	irpos.tfg_to_joint_position(0.055, 5.0)
	irpos.move_rel_to_cartesian_pose_with_contact(4.0, Pose(Point(0, 0, 0.08), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(6.0,6.0,6.0),Vector3(0.0,0.0,0.0)))
	rect_size=0.005
	
	#gora prawo
	irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(rect_size, -rect_size, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
	#dol prawo
	irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(-rect_size, -rect_size, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
	#dol lewo
	irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(-rect_size, rect_size, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
	#gora lewo
	irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(rect_size, rect_size, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
	
	
	if mod=="CROSS":
		#dol
		irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(-rect_size/2, 0, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
		#2gora
		irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(rect_size, 0, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
		#dol
		irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(-rect_size/2, 0, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
		#lewo
		irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(0, -rect_size/2, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
		#2prawo
		irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(0, rect_size, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
		#lewo
		irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(0, -rect_size/2, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
		
		
	#push
	irpos.move_rel_to_cartesian_pose_with_contact(7.0, Pose(Point(0, 0, 0.08), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(11.0,11.0,11.0),Vector3(0.0,0.0,0.0)))
	
	#go up
	irpos.move_rel_to_cartesian_pose_with_contact(5.0, Pose(Point(0, 0, -0.05), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
	
	#push
	irpos.move_rel_to_cartesian_pose_with_contact(7.0, Pose(Point(0, 0, 0.08), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(11.0,11.0,11.0),Vector3(0.0,0.0,0.0)))
		
def service_position():
	#print irpos.get_joint_position()
	if  irpos.get_joint_position() != [ 7.412760409739285e-06, -1.764427006069524, 0.0006186793623569331, 0.1930235079212923, 4.7123619308455735, 1.48]:
		irpos.move_to_joint_position([ 7.412760409739285e-06, -1.764427006069524, 0.0006186793623569331, 0.1930235079212923, 4.7123619308455735, 1.48], 10.0)
	else:
		print "Move along."
	irpos.tfg_to_joint_position(0.09, 5.0)
	rospy.sleep(2)
	
def move_overboard():
	global Board
	global Overboard
	if Overboard==-1:
		if Board==[]:
			print("No board in sight!")
			return -1
		else:
			print "BOARD DATA HERE:"
			print Board
			move_over(Board[1], Board[2], Board[3])
			irpos.move_rel_to_cartesian_pose_with_contact(20.0, Pose(Point(0, 0, 0.3), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(6.0,6.0,6.0),Vector3(0.0,0.0,0.0)))
			rospy.sleep(1)
			#irpos.move_rel_to_cartesian_pose_with_contact(20.0, Pose(Point(0, 0, -0.2), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(6.0,6.0,6.0),Vector3(0.0,0.0,0.0)))
	
			irpos.move_rel_to_cartesian_pose(15.0, Pose(Point(0, 0, -0.2), Quaternion(0.0, 0.0, 0.0, 1.0)))
	
			Overboard=irpos.get_joint_position()
			lst = list(Overboard)
			lst.append(10.0)
			Overboard = tuple(lst)
			return 0
	else:
		print "MOVING OVERBOARD"
		irpos.move_to_joint_position(Overboard, 5)
		return 1
    
def move_operation(): 
	global Reds
	global Greens
	global Blues  
	schema = model.open_schema()
	print schema
	level=0
	service_position()
	rospy.sleep(3)
	for i1 in schema:
		dist=-3
		for i2 in i1:
			if i2[1] == '.':
				dist=dist+int(i2[0])
				#print ". dist = " + str(dist)
				continue
			#new_brick = choose_block(i2[1],i2[0])
			dist=dist+(int(i2[0])/2)-1
			#print "afterbrick dist = " + str(dist)
			#if new_brick == 'ERROR':
			#	print "ERROR"
			#	return 'No brick found'
			print "taking"
			print dist
			print level
			#take_operation(new_brick[1],new_brick[2],new_brick[3],dist,i2[1],i2[0])
			take_operation(i2[1],i2[0],dist,level)
			print "taking ended"
			
			dist=dist+(int(i2[0])/2)+1
			#print "afterall dist = " + str(dist)
		level=level+1
	
def take_operation(colour, siz, offset=0, heigth=0):#move_x, move_y, rads, 
	new_brick = choose_block(colour,siz, 'FURTHEST')
	print "New brick to take:" + str(new_brick)
	if new_brick == 'ERROR':
		print "ERROR"
		return 'No brick found'
	move_x=new_brick[1]
	move_y=new_brick[2]
	rads=new_brick[3]
	#MOVE OVER
	move_over(move_x, move_y, rads)
	
	rospy.sleep(2)
	new_brick = choose_block(colour,siz, 'CLOSEST')
	if new_brick == 'ERROR':
		print "ERROR"
		return 'No brick found'
	move_x=new_brick[1]
	move_y=new_brick[2]
	rads=new_brick[3]
	#CORRECT
	move_over(move_x, move_y, rads, 5.0)
	grab_brick()
	rospy.sleep(2)
	#Bring back the block
	put_brick(offset, heigth)
	#push
	push_brick()
	#return to service position
	service_position()
	rospy.sleep(2)
	
	return "PLACING " + str(colour) + str(siz) + " ENDED"
	
def move_operation_2():
	global first_time
	global move_x
	global move_y
	global rads
	global BlockPos
	DataLock.acquire()
	data = BlockPos
	DataLock.release()
	print data
	
	print [central_pos(data[1:5]),central_pos(data[5:9])]
	scale_rotation(data[1:5],data[5:9])
	if first_time==0:
		print "FIRST STAGE"
		move_over(move_x, move_y, rads)
		first_time=first_time+1
		rospy.sleep(2)
		return
		
	if first_time==1:
		print "SECOND STAGE"
		#correction(move_x, move_y, rads)
		first_time=first_time+1
		return
		
	if first_time==2:
		print "THIRD STAGE"
		grab_brick()
		rospy.sleep(2)
		#Bring back the block
		put_brick()
		#push
		push_brick()
		#return to service position
		service_position()
		first_time=first_time+1
		return
		
	if first_time==3:
		exit()
		
if __name__ == '__main__':
	irpos = IRPOS("thIRpOS", "Irp6p", 6, 'irp6p_manager') #z csn
	service_position()
	irpos.move_rel_to_cartesian_pose_with_contact(5.0, Pose(Point(0, 0, 0.035), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
	rospy.Subscriber("float32MultiArray", Float32MultiArray, callback, None, 1)
	listener()

