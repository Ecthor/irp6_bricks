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
global moving



def main():
	markerArray = MarkerArray()
	while not rospy.is_shutdown():
		markerArray = MarkerArray()
		for i in bricks:
			for j in i:
				if j==0:
					continue
				markerArray.markers.append(j)
		#print "----------------------------"
		#for i in bricks:
		#	for j in i:
		#		if j==0:
		#			continue
		#		print "[ " + str(j.color.r) +str(j.color.g) +str(j.color.b) + ' ]'
		#print "----------------------------"
		#print height
		id = 0
		for m in markerArray.markers:
			m.id = id
			id += 1
		

		# Publish the MarkerArray
		publisher.publish(markerArray)
		rospy.sleep(1)

def get_board_pos():
	global bricks
	global height
	listener = tf.TransformListener()
	i=0
	while(i<100):
		try:
			(trans,rot) = listener.lookupTransform('/pl_base', '/pl_6', rospy.Time(0))
		except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
			i=i+1
			time.sleep(1)
			continue
		break
		
	DataLock.acquire()
	bricks[0][0].header.frame_id = "/pl_base"
	bricks[0][0].pose.position.x=trans[0]
	bricks[0][0].pose.position.y=trans[1]
	bricks[0][0].pose.position.z=trans[2]-0.54
	height=trans[2]-0.54
	for i in bricks:
		for j in i:
			if j==0:
				continue
			j.pose.position.z=height
	DataLock.release()
	
def rearrange(col,data):
	global bricks
	DataLock.acquire()
	if bricks[col]!=[0]:
		DataLock.release()
		return
	bricks[col]=[0]
	DataLock.release()
	print data
	table=eval(data[1])
	for i in table:
		marker = Marker()
		marker.type = marker.CUBE
		marker.action = marker.ADD
		marker.scale.x = 0.034*(i[0]/2)
		marker.scale.y = 0.034
		marker.scale.z = 0.023
		if col == 1:
			marker.color.a = 1.0
			marker.color.r = 1.0
			marker.color.g = 0.0
			marker.color.b = 0.0
		if col == 2:
			marker.color.a = 1.0
			marker.color.r = 0.0
			marker.color.g = 1.0
			marker.color.b = 0.0
		if col == 3:
			marker.color.a = 1.0
			marker.color.r = 0.0
			marker.color.g = 0.0
			marker.color.b = 1.0
		marker.pose.orientation.w = 0.0
		#marker.pose.orientation.z = i[3]
		j=0
		trans=[0,0,0]
		rot=[0,0,0]
		listener = tf.TransformListener()
				
		while(j<2):
			try:
				(trans,rot) = listener.lookupTransform('/pl_base', '/pl_6', rospy.Time(0))
			except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
				j=j+1
				time.sleep(0.1)
				print "exception!"
				continue
			break
		marker.header.frame_id = "/pl_base"
		marker.pose.position.x=trans[0]+i[1]
		marker.pose.position.y=trans[1]-i[2]
		marker.pose.orientation.x = 0.0#rot[0]
		marker.pose.orientation.y = 0.0#rot[1]
		#marker.pose.orientation.z = rot[2]-i[3]
		marker.pose.orientation.z = float(i[3])#i[3]*pi/2
		marker.pose.orientation.w = 1.0
		global height
		marker.pose.position.z=height
		DataLock.acquire()
		bricks[col].append(marker)
		DataLock.release()
		
		
def grab():
	global moving
	listener = tf.TransformListener()
	err=0
	while(err<2):
		try:
			(trans,rot) = listener.lookupTransform('/pl_base', '/pl_6', rospy.Time(0))
		except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
			err=err+1
			time.sleep(0.1)
			continue
		break
	moving = [1,0]
	print "Bricks"
	print bricks
	for i in bricks:
		for j in i:
			print "cosen "
			print j
			if (math.fabs(trans[0])+math.fabs(trans[1]))-(math.fabs(j.pose.position.x)+math.fabs(j.pose.position.y))<(math.fabs(trans[0])+math.fabs(trans[1]))-(math.fabs((bricks[moving[0]][moving[1]]).pose.position.x)+math.fabs((bricks[moving[0]][moving[1]]).pose.position.y)):
				moving=[i,j]
	(bricks[moving[0]][moving[1]]).pose.position.x=0
	(bricks[moving[0]][moving[1]]).pose.position.y=0
	(bricks[moving[0]][moving[1]]).pose.position.z=-0.56
	(bricks[moving[0]][moving[1]]).header.frame_id = "/pl_6"
def put():
	global moving
	listener = tf.TransformListener()
	err=0
	while(err<2):
		try:
			(trans,rot) = listener.lookupTransform('/pl_base', '/pl_6', rospy.Time(0))
		except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
			err=err+1
			time.sleep(0.1)
			continue
		break
		print "Bricks"
		print bricks
	print "cosen "
	print bricks[moving[0]][moving[0]]
	(bricks[moving[0]][moving[1]]).pose.position.x=trans[0]
	(bricks[moving[0]][moving[1]]).pose.position.y=trans[1]
	(bricks[moving[0]][moving[1]]).pose.position.z=trans[2]
	(bricks[moving[0]][moving[1]]).header.frame_id = "/pl_base"

def callback(data):
	global bricks
	global height
	data=data.data
	data = data.split(";")
	if str(data[0])=="Board":
		#print "Board data"
		marker = Marker()
		marker.header.frame_id = "/pl_base"
		marker.type = marker.CUBE
		marker.action = marker.ADD
		marker.scale.x = 0.1272
		marker.scale.y = 0.1272
		marker.scale.z = 0.01
		marker.color.a = 1.0
		marker.color.r = 1.0
		marker.color.g = 1.0
		marker.color.b = 0.2
		marker.pose.orientation.w = 1.0
		marker.pose.position.x = 0
		marker.pose.position.y = 0
		marker.pose.position.z = 0
		marker.pose.orientation.z = 0
		if str(data[1])=="rotation":
			marker.pose.orientation.z=float(data[2])
			DataLock.acquire()
			bricks[0][0]=marker
			DataLock.release()
		if data[1]=="position":
			get_board_pos()
	if str(data[0])=="Reds":
		#print "Redds data"
		rearrange(1,data)
	if str(data[0])=="Greens":
		#print "Greens data"
		rearrange(2,data)
	if str(data[0])=="Blues":
		#print "Blues data"
		rearrange(3,data)
	if str(data[0])=="Grabbing":
		grab()
		print "Grab"
	if str(data[0])=="Putting":
		put()
		print "Put"
	return

if __name__ == '__main__':
	topic = 'visualization_marker_bricks'
	publisher = rospy.Publisher(topic, MarkerArray)
	rospy.Subscriber("rviz_brick_info", String, callback, None, 5)
	rospy.init_node('register_bricks')
	main()
