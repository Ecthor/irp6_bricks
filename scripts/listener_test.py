#!/usr/bin/env python


import rospy
import math

from std_msgs.msg import Float32MultiArray

global move_x
move_x=0
global move_y
move_y=0
global rads
rads=0

def central_pos(x):
	print x
	return (x[0]+x[1]+x[2]+x[3])/len(x)
	
def rotation(xy):
	if xy[0]<xy[1]:
		print 'obrot w prawo'
		alpha=math.fabs(xy[3]-xy[2])/math.fabs(xy[1]-xy[0]) #dx/dy
	else:
		print 'obrot w lewo'
		alpha=math.fabs(xy[1]-xy[0])/math.fabs(xy[3]-xy[2]) #dx/dy
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
	move_x=move_x/100
	move_y=move_y/100
	rads = rotation(dist_max_val)
	print 'rotation: '
	print rotation(dist_max_val)
			
	
def callback(data):
	rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
	print [central_pos(data.data[1:5]),central_pos(data.data[5:9])]
	scale_rotation(data.data[1:5],data.data[5:9])
	print 'test ' + str(move_x) 
	
	
def listener():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # node are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'talker' node so that multiple talkers can
    # run simultaneously.
    rospy.init_node('listenerbricks', anonymous=True)

    rospy.Subscriber("float32MultiArray", Float32MultiArray, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()

