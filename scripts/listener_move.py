#!/usr/bin/env python


from irpos import *
import rospy
import math

from std_msgs.msg import Float32MultiArray

global move_x
move_x=0
global move_y
move_y=0
global rads
rads=0
global first_time
first_time=0

def createPose(x, y, z, ox, oy, oz, ow):
	position = Point(x, y, z)
	quaternion = Quaternion(ox, oy, oz, ow)

	P = Pose(position, quaternion)
	return P
	
def central_pos(x):
	print x
	return (x[0]+x[1]+x[2]+x[3])/len(x)
	
def rotation(xy):
	alpha=math.fabs(xy[1]-xy[0])/math.fabs(xy[3]-xy[2])
	return math.atan(alpha)
	
	
def scale_rotation(x,y):
	global move_x
	global move_y
	global rads
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
	print 'Scale: ' + str(dist_min) + ' = 3,1cm'
	move_y=((655-central_pos(x))*3.1)/dist_min
	move_x=((637-central_pos(y))*3.1)/dist_min
	print 'Distance x: ' + str(move_x) + ' cm'
	print 'Distance y: ' + str(move_y) + ' cm'
	move_y=-move_y/100
	move_x=move_x/100
	rads = rotation(dist_max_val)
	print 'rotation: '
	print rotation(dist_max_val)
	print irpos.get_tfg_joint_position()
			
	
def callback(data):
	global first_time
	rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
	print [central_pos(data.data[1:5]),central_pos(data.data[5:9])]
	scale_rotation(data.data[1:5],data.data[5:9])
	if first_time==0:
		irpos.move_rel_to_cartesian_pose_with_contact(6.0, Pose(Point(move_x, move_y, 0), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(4.0,4.0,4.0),Vector3(0.0,0.0,0.0)))
		myjoint = irpos.get_joint_position()
		lst = list(myjoint)
		lst[5] = lst[5]-rads
		myjoint = tuple(lst)
		print myjoint
		irpos.move_to_joint_position(myjoint, 8.0)
		first_time=first_time+1
		
	if (move_x > 0.005 or move_y > 0.005) and (first_time==1):
		#irpos.tfg_to_joint_position(2, 10.0)
		irpos.move_rel_to_cartesian_pose_with_contact(6.0, Pose(Point(0, 0, -0.8), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(5.0,5.0,5.0),Vector3(0.0,0.0,0.0)))
		#irpos.tfg_to_joint_position(0.003, 10.0)
		irpos.move_rel_to_cartesian_pose_with_contact(6.0, Pose(Point(0, 0, 0.2), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(5.0,5.0,5.0),Vector3(0.0,0.0,0.0)))
		first_time=first_time+1
	
def listener():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # node are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'talker' node so that multiple talkers can
    # run simultaneously.
    #rospy.init_node('listenerbricks', anonymous=True)
    print "Check position"
    print irpos.get_tfg_joint_position()

    rospy.Subscriber("float32MultiArray", Float32MultiArray, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
	irpos = IRPOS("thIRpOS", "Irp6p", 6, 'irp6p_manager') #z csn
	irpos.move_to_joint_position([ 7.412760409739285e-06, -1.764427006069524, 0.0006186793623569331, 0.1930235079212923, 4.7123619308455735, 1.5707923033898181], 8.0)
	
	listener()

