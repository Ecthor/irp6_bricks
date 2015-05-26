#!/usr/bin/env python


from irpos import *
import rospy
import math
import sys
import threading

from std_msgs.msg import Float32MultiArray

DataLock = threading.Lock()
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
global Reds
global Greens
global Blues
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
	#print 'Scale: ' + str(dist_min) + ' = 3,1cm'
	move_x=((655-central_pos(x))*3.1)/dist_min #655
	move_y=((655-central_pos(y))*3.1)/dist_min #637 650
	#print 'Distance x: ' + str(move_x) + ' cm'
	#print 'Distance y: ' + str(move_y) + ' cm'
	move_y=-move_y/100
	move_x=move_x/100
	rads = rotation(dist_max_val)
	#print 'rotation: '
	#print rotation(dist_max_val)
	#print irpos.get_tfg_joint_position()
			
	
def callback(data):
	global BlockPos
	# DATA: num,y1,y2,y3,y4,x1,x2,x3,x4
	#rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
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
		correction(move_x, move_y, rads)
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
	rospy.Subscriber("float32MultiArray", Float32MultiArray, callback)
	listener()

