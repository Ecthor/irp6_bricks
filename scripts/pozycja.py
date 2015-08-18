#!/usr/bin/env python
from irpos import *

import math
import threading

dataLock = threading.Lock()

lastData = None

def callback(data):
	global lastData
	dataLock.acquire()
	lastData = data.data
	dataLock.release()


if __name__ == '__main__':

	#topic = 'visualization_marker_array'
	#publisher = rospy.Publisher(topic, Marker)	

	rospy.Subscriber("pnp", Float32MultiArray, callback)
	irpos = IRPOS("publikowanie_rogu", "Irp6ot", 7, "irp6ot_manager")

