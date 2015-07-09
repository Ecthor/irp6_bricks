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
def central_pos(x):
	print x
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
			print 'obrot w prawo'
			#alpha=-math.fabs(xy[3]-xy[2])/math.fabs(xy[1]-xy[0]) #dx/dy
			alpha=-math.fabs(xy[1]-xy[0])/math.fabs(xy[3]-xy[2]) #dx/dy
			print math.atan(alpha)
			if math.atan(alpha)<-1:
				print "PRZEKROCZONE w prawo"
				return math.atan(alpha)+3.1415
		else:
			print 'obrot w lewo'
			#alpha=math.fabs(xy[3]-xy[2])/math.fabs(xy[1]-xy[0]) #dx/dy
			alpha=math.fabs(xy[1]-xy[0])/math.fabs(xy[3]-xy[2]) #dx/dy
			print math.atan(alpha)
		return math.atan(alpha)
	except:
		print "Divided by zero, vertical line, assuming zero"
		return 0
	
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
	#size, dx,dy
	dist = math.sqrt( (x[3] - x[0])**2 + (y[3] - y[0])**2 )
	if dist_min > dist:
		dist_min=dist
		dist_min_pos = [x[3],x[0],y[3],y[i+1]]
	if dist_max < dist:
		dist_max = dist
		dist_max_pos = [x[3],x[0],y[3],y[0]]
	move_y=-((655-central_pos(x))*3.1*scale_modifier)/(dist_min*100)
	move_x=((637-central_pos(y))*3.1*scale_modifier)/(dist_min*100)
	size=round(dist_max/dist_min)*2
	rot=rotation(dist_max_pos)
	#print "Pos X"
	#print x
	#print "Pos Y"
	#print y
	#print "Rotation"
	#print rot
	return [size,move_x,move_y,rot]


def rearrange(data):
	'''print("dlugosc") 
	print(len(data))
	print("kolor") 
	print(data[0])
	for i in data:
	print(info(data[1:5],data[5:9]))
	return "test"'''
	if data[0] == 0:
		return
		global Board
		#if Board==[]:
		Board = info(data[1:5],data[5:9],4)
		print("BOARD DATA HERE")
		print(Board)
		return "Received Board data"
	global Reds
	global Greens
	global Blues
	rows=len(data)
	print(rows)
	table=[]
	i=0
	#print("kolor") 
	#print(data[0])
	while i<rows:
		#print data[i]
		table.append(info(data[i+1:i+5],data[i+5:i+9]))
		#print info(data[i+1:i+5],data[i+5:i+9])
		i=i+9;
	print(table)
	if data[0] == 1:
		Reds=table
		return "Received Reds data"
	elif data[0] == 2:
		Greens=table
		return "Received Greens data"
	elif data[0] == 3:
		Blues=table
		return "Received Blues data"
	
def scale_rotation(x,y):
	global move_x
	global move_y
	global rads
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
	#print 'Scale: ' + str(dist_min) + ' = 3,1cm'
	move_y=((655-central_pos(x))*3.1)/dist_min
	move_x=((637-central_pos(y))*3.1)/dist_min
	#print 'Distance x: ' + str(move_x) + ' cm'
	#print 'Distance y: ' + str(move_y) + ' cm'
	move_x=move_x/100
	move_y=move_y/100
	rads = rotation(dist_max_pos)
	#print 'rotation: '
	#print rotation(dist_max_pos)
			
	
def callback(data):
	global rads
	global Reds
	global Greens
	global Blues
	global Board
	#rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
	
	if data.data==():
		return "NO DATA RECEIVED IN PACKAGE"
	#print [central_pos(data.data[1:5]),central_pos(data.data[5:9])]
	scale_rotation(data.data[1:5],data.data[5:9])
	#print 'test ' + str(move_x) 
	#print(rearrange(data.data))
	rearrange(data.data)
	print("Reds")
	print(Reds)
	print("Greens")
	print(Greens)
	print("Blues")
	print(Blues)
	print("Board")
	print(Board)
	
def listener():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # node are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'talker' node so that multiple talkers can
    # run simultaneously.
    rospy.init_node('listenerbricks', anonymous=True)


    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
	rospy.Subscriber("float32MultiArray", Float32MultiArray, callback, None, 1)
	listener()

