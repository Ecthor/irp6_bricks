#!/usr/bin/env python
from irpos import *

if __name__ == '__main__':
	#irpos = IRPOS("IRpOS", "Irp6p", 6)
	irpos = IRPOS("thIRpOS", "Irp6p", 6, 'irp6p_manager') #z csn
	
	irpos.move_to_synchro_position(10.0)

	#poruszanie motorami	
	#irpos.move_to_motor_position([6.116680896539328, 8.65822935329347, -34.55437759683414, 191.310097771172, 140.33868871754868, 745.4779455482828], 10.0)

	#poruszanie jointmi
	#irpos.move_to_joint_position([-0.13933613987476287, -1.4916385652871773, -0.22970620274142098, -0.16194261686533928, 4.5, -0.2], 10.0)

	#poruszanie chytakiem
	#1. rozstaw w m, 2. czas
	#irpos.tfg_to_joint_position(0.07, 5.0)

	#ustawianie reczne - sterowanie silowe
	#poczatek sterowania silowego
	##irpos.set_tool_physical_params(10.8, Vector3(0.004, 0.0, 0.156))
	#irpos.start_force_controller(Inertia(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)), ReciprocalDamping(Vector3(0.0025, 0.0025, 0.0025), Vector3(0.0, 0.0, 0.0)), Wrench(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)), Twist(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)))

	#time.sleep(30.0)
	#print irpos.get_motor_position()
	#irpos.stop_force_controller()
	#koniec sterowania silowego
	

	#1.ustawiamy chytak do pozycji roboczej
	#irpos.move_to_joint_position([-0.05958721029640646, -1.6148335928772972, 0.06109786284141526, -0.048274545057386486, 4.725347612820872, -0.06940834400104375], 10.0)
	#irpos.move_to_motor_position([6.7151542970481835, 35.89583765991698, 8.898561191293089, 151.30852697484522, 70.34025951387547, 749.6374142216357], 10.0)
	#2. rozszerz chytak
	#irpos.tfg_to_joint_position(0.07, 5.0)
	#3.idz na dol 2.0 N, 40 cm w dol
	#irpos.move_rel_to_cartesian_pose_with_contact(20.0, Pose(Point(0.0, 0.0, -0.4), Quaternion(0.0, 0.0, 0.0, 0.0)), Wrench(Vector3(0.0,0.0,2.0),Vector3(0.0,0.0,0.0)))
	#lekko w gore
	#irpos.move_rel_to_cartesian_pose(10.0, Pose(Point(0.0, 0.0, 0.005), Quaternion(0.0, 0.0, 0.0, 1)))
	#lap
	#irpos.tfg_to_joint_position(0.063, 5.0)
	#przeies sie do pozycji 1
	#irpos.move_to_motor_position([1.8802432031734913, 27.60674544342031, -17.354157818430018, 151.310097771172, 70.3308347359147, 758.4904223194518], 10.0)

	#print irpos.get_joint_position()
	#irpos.tfg_to_joint_position(0.09, 5.0)
	#irpos.tfg_to_joint_position(0.073, 5.0)

	#print irpos.get_cartesian_pose()
	#print irpos.get_tfg_joint_position()
	#print irpos.get_tfg_motor_position()
	

	print "OK"

	
#pozycja w motorach nad pionkiem
#6.7151542970481835, 35.89583765991698, 8.898561191293089, 151.30852697484522, 70.34025951387547, 749.6374142216357
