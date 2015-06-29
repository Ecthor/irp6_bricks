#!/usr/bin/env python

from Tkinter import Tk
from tkFileDialog import askopenfilename

def open_schema():
	Tk().withdraw()
	filename = askopenfilename()
	print(filename)

	file=open(filename, "r")
	position = file.read()
	print(position)

	position = position.split('\n')
	lista=[]
	for a in position:
		if a!='':
			lista.append(a.split(','))

	lista2=[]
	for a in lista:
		temp=[]
		for b in a:
			temp.append(b.split(' '))
		lista2.append(temp)
	print lista2

	#PRINT
	out=''
	for a in lista2:
		for b in a:
			for x in range(0,int(b[0])):
				out=out+b[1]
		out = out + '\n'
	print out

	file.close()
	return list(reversed(lista2))
	
