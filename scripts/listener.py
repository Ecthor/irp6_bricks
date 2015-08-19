#!/usr/bin/env python
from irpos import *
from std_msgs.msg import *
from visualization_msgs.msg import Marker
from visualization_msgs.msg import MarkerArray
import threading
import math
import time

DataLock = threading.Lock()
global bricks
bricks=[[0],[0],[0],[0]]
height=0



def main():
	
		rospy.spin()



def callback(data):
	global bricks
	global height
	data=data.data
	data = data.split(";")
	print data
	if str(data[0])=="Board":
		print "BOARD DATA HERE!"

if __name__ == '__main__':
	topic = 'visualization_marker_bricks'
	publisher = rospy.Publisher(topic, MarkerArray)
	rospy.Subscriber("rviz_brick_info", String, callback, None, 5)
	rospy.init_node('register_bricks_test')
	main()
