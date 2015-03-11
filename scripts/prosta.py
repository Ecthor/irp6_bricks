#!/usr/bin/env python
from irpos import *
import math

def createPose(x, y, z, ox, oy, oz, ow):
	position = Point(x, y, z)
	quaternion = Quaternion(ox, oy, oz, ow)

	P = Pose(position, quaternion)
	return P

if __name__ == '__main__':
	#irpos = IRPOS("thIRpOS", "Irp6p", 6) #bez csn
	irpos = IRPOS("thIRpOS", "Irp6p", 6, 'irp6p_manager') #z csn

	

	irpos.move_to_joint_position([ 0, -0.5 * math.pi, 0, 0, 1.5 * math.pi, -0.5 * math.pi], 12.0)
	
	#irpos.tfg_to_joint_position(0.069, 10.0)
	#irpos.move_rel_to_cartesian_pose_with_contact(5.0, Pose(Point(-0.05, 0, 0), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(4.0,4.0,4.0),Vector3(0.0,0.0,0.0)))
	
	
	#print irpos.get_tfg_joint_position()
	
	#irpos.move_rel_to_cartesian_pose_with_contact(12.0, Pose(Point(0.2, 0.2, -0.1), Quaternion(0.0, 0.0, 0.0, 1.0)), Wrench(Vector3(4.0,4.0,4.0),Vector3(0.0,0.0,0.0)))
	#irpos.move_rel_to_cartesian_pose(10.0, Pose(Point(0.0, 0.0, -0.05), Quaternion(0.0, 0.0, 0.0, 1.0)))

	print "OK"
