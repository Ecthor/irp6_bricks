#!/usr/bin/env python
from irpos import *
import math

if __name__ == '__main__':
	#irpos = IRPOS("IRpOS", "Irp6p", 6)
	irpos = IRPOS("thIRpOS", "Irp6p", 6, 'irp6p_manager') #z csn
	#irpos.move_to_synchro_position(10.0)
	irpos.move_to_joint_position([ 7.412760409739285e-06, -1.764427006069524, 0.0006186793623569331, 0.1930235079212923, 4.7123619308455735, 1.48], 15.0)
	irpos.tfg_to_joint_position(0.06, 5.0)
	
	print "OK"

#stara pozycja
#irpos.move_to_joint_position([ 7.412760409739285e-06, -1.764427006069524, 0.0006186793623569331, 0.1930235079212923, 4.7123619308455735, 1.5707923033898181], 10.0)
#pozycja w motorach nad pionkiem
#6.7151542970481835, 35.89583765991698, 8.898561191293089, 151.30852697484522, 70.34025951387547, 749.6374142216357
