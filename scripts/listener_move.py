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
	print x
	return (x[0]+x[1]+x[2]+x[3])/len(x)
	
def rotation(xy):
	if xy[3]<xy[2]:
		print 'obrot w prawo'
		alpha=-math.fabs(xy[3]-xy[2])/math.fabs(xy[1]-xy[0]) #dx/dy
		print math.atan(alpha)
		if math.atan(alpha)<-1:
			print "PRZEKROCZONE"
			return math.atan(alpha)+3.1415
	else:
		print 'obrot w lewo'
		alpha=math.fabs(xy[3]-xy[2])/math.fabs(xy[1]-xy[0]) #dx/dy
		print math.atan(alpha)
	return math.atan(alpha)
	
def choose_block(colour, siz):
	if colour == "b":
		TableLock.acquire()
		for i in Blues:
			if i[0]==siz:
				return i
		TableLock.release()
	elif colour== "r":
		TableLock.acquire()
		for i in Reds:
			if i[0]==siz:
				return i
		TableLock.release()
	elif colour== "g":
		TableLock.acquire()
		for i in Greens:
			if i[0]==siz:
				return i
		TableLock.release()
	
def info(x,y, scale_modifier=1):
	dist_min = math.sqrt( (x[0] - x[1])**2 + (y[0] - y[1])**2 )
	dist_min_val = [x[0],x[1],y[0],y[1]]
	dist_max = math.sqrt( (x[0] - x[1])**2 + (y[0] - y[1])**2 )
	dist_max_val = [x[0],x[1],y[0],y[1]]
	for i in range(1,3):
		dist = math.sqrt( (x[i] - x[i+1])**2 + (y[i] - y[i+1])**2 )
		if dist_min > dist:
			dist_min=dist
			dist_min_val = [x[i],x[i+1],y[i],y[i+1]]
		if dist_max < dist:
			dist_max = dist
			dist_max_val = [x[i],x[i+1],y[i],y[i+1]]
	#size, dx,dy
	move_y=-((655-central_pos(x))*3.1*scale_modifier)/(dist_min*100)
	move_x=((637-central_pos(y))*3.1*scale_modifier)/(dist_min*100)
	size=round(dist_max/dist_min)*2
	rot=rotation(dist_max_val)
	return [size,move_x,move_y,rot]
	
def rearrange(data):
	print("REARRANGE")
	print(data)
	if data==():
		return "NO DATA RECEIVED IN PACKAGE"
	if data[0] == 0:
		global Board
		if Board==[]:
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
	print(table)
	
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
	dist_min_val = [x[0],x[1],y[0],y[1]]
	dist_max = math.sqrt( (x[0] - x[1])**2 + (y[0] - y[1])**2 )
	dist_max_val = [x[0],x[1],y[0],y[1]]
	for i in range(1,3):
		dist = math.sqrt( (x[i] - x[i+1])**2 + (y[i] - y[i+1])**2 )
		if dist_min > dist:
			dist_min=dist
			dist_min_val = [x[i],x[i+1],y[i],y[i+1]]
		if dist_max < dist:
			dist_max = dist
			dist_max_val = [x[i],x[i+1],y[i],y[i+1]]
	move_x=((655-central_pos(x))*3.1)/dist_min #655
	move_y=((655-central_pos(y))*3.1)/dist_min #637 650
	move_y=-move_y/100
	move_x=move_x/100
	rads = rotation(dist_max_val)
			
def callback(data):
	global BlockPos
	# DATA: num,y1,y2,y3,y4,x1,x2,x3,x4
	#rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
	print(rearrange(data.data))
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
		while Overboard==-1:
			print("EXTERMINATE")
			move_overboard()
		global BlockPos
		#print "Check position"	
		#print irpos.get_tfg_joint_position()
		
		#print "Trying move_operation"
		DataLock.acquire()
		if BlockPos != []:
			DataLock.release()
			print "YEAH"
			move_operation()
			autostop=0
		else:
			DataLock.release()
			autostop+=1
			rospy.sleep(0.01)
			if autostop>1000:
				print "CONNECTION TIMEOUT. STOP"
				break
	# spin() simply keeps python from exiting until this node is stopped
	#rospy.spin()
	
def move_over(move_x, move_y, rads):
    irpos.move_rel_to_cartesian_pose_with_contact(17.0, Pose(Point(move_x, move_y, 0), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
    rotate(rads)
    #move down to correct
    irpos.move_rel_to_cartesian_pose_with_contact(5.0, Pose(Point(0, 0, 0.05), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
    return

def rotate(rads):
    myjoint = irpos.get_joint_position()
    lst = list(myjoint)
    lst[5] = lst[5]-rads
    myjoint = tuple(lst)
    irpos.move_to_joint_position(myjoint, 8.0)
    return
    
def correction(move_x, move_y, rads):
	if move_x<0.05:# and move_x>0.0005:
		print "Correcting x"
		irpos.move_rel_to_cartesian_pose_with_contact(3.0, Pose(Point(move_x, 0, 0), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
	if move_y<0.05:# and move_y>0.0005:
		print "Correcting y"
		irpos.move_rel_to_cartesian_pose_with_contact(3.0, Pose(Point(0, move_y, 0), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
	print rads
	if math.fabs(rads)<1 and math.fabs(rads)>0.05:
		print "Correcting rotation"
		rotate(rads)
		
def grab_brick():
	irpos.tfg_to_joint_position(0.09, 5.0)
	irpos.move_rel_to_cartesian_pose_with_contact(20.0, Pose(Point(0, 0, 0.3), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(7.0,7.0,7.0),Vector3(0.0,0.0,0.0)))
	irpos.move_rel_to_cartesian_pose_with_contact(6.0, Pose(Point(0, 0, -0.005), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
	irpos.tfg_to_joint_position(0.073, 5.0)
	irpos.move_rel_to_cartesian_pose_with_contact(10.0, Pose(Point(0, 0, -0.2), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
	irpos.move_to_joint_position([ 7.412760409739285e-06, -1.764427006069524, 0.0006186793623569331, 0.1930235079212923, 4.7123619308455735, 1.5707923033898181], 10.0)
	
def put_brick():
	move_overboard()
	irpos.move_rel_to_cartesian_pose_with_contact(20.0, Pose(Point(0, 0, 0.3), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(6.0,6.0,6.0),Vector3(0.0,0.0,0.0)))
	#irpos.move_rel_to_cartesian_pose_with_contact(3.0, Pose(Point(0, 0, -0.005), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(6.0,6.0,6.0),Vector3(0.0,0.0,0.0)))
	print "Open"
	irpos.tfg_to_joint_position(0.09, 5.0)
	irpos.move_rel_to_cartesian_pose_with_contact(3.0, Pose(Point(0, 0, -0.005), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(6.0,6.0,6.0),Vector3(0.0,0.0,0.0)))
	
	irpos.move_rel_to_cartesian_pose_with_contact(5.0, Pose(Point(0, 0, -0.05), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
	
def push_brick():
	irpos.tfg_to_joint_position(0.055, 5.0)
	irpos.move_rel_to_cartesian_pose_with_contact(4.0, Pose(Point(0, 0, 0.08), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(6.0,6.0,6.0),Vector3(0.0,0.0,0.0)))
	
	#gora prawo
	irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(0.008, -0.008, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
	#irpos.move_rel_to_cartesian_pose_with_contact(3.0, Pose(Point(0.008, -0.008, 0), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(12.0,12.0,12.0),Vector3(0.0,0.0,0.0)))
	
	#dol prawo
	irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(-0.008, -0.008, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
	#irpos.move_rel_to_cartesian_pose_with_contact(3.0, Pose(Point(0.008, -0.008, 0), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(12.0,12.0,12.0),Vector3(0.0,0.0,0.0)))
	
	#dol lewo
	irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(-0.008, 0.008, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
	#irpos.move_rel_to_cartesian_pose_with_contact(3.0, Pose(Point(-0.008, 0.008, 0), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(12.0,12.0,12.0),Vector3(0.0,0.0,0.0)))
	
	#gora lewo
	irpos.move_rel_to_cartesian_pose(3.0, Pose(Point(0.008, 0.008, 0), Quaternion(0.0, 0.0, 0.0, 1.0)))
	#irpos.move_rel_to_cartesian_pose_with_contact(3.0, Pose(Point(-0.008, 0.008, 0), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(12.0,12.0,12.0),Vector3(0.0,0.0,0.0)))
	
	#push
	irpos.move_rel_to_cartesian_pose_with_contact(7.0, Pose(Point(0, 0, 0.08), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(11.0,11.0,11.0),Vector3(0.0,0.0,0.0)))
	
	#go up
	irpos.move_rel_to_cartesian_pose_with_contact(5.0, Pose(Point(0, 0, -0.05), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(9.0,9.0,9.0),Vector3(0.0,0.0,0.0)))
	
	#push
	irpos.move_rel_to_cartesian_pose_with_contact(7.0, Pose(Point(0, 0, 0.08), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(11.0,11.0,11.0),Vector3(0.0,0.0,0.0)))
		
def service_position():
	print irpos.get_joint_position()
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
			move_over(Board[1], Board[2], Board[3])
			Overboard=irpos.get_joint_position()
			return 0
	else:
		irpos.move_to_joint_position(Overboard)
		return 1
    
def move_operation_2():  
	global Reds
	global Greens
	global Blues  
	schema = model.open_schema()
	
	
def move_operation():
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
	rospy.Subscriber("float32MultiArray", Float32MultiArray, callback)
	listener()

