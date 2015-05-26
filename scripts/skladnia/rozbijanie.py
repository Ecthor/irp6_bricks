#!/usr/bin/env python

from Tkinter import Tk
from tkFileDialog import askopenfilename

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
print(lista)



file.close()
