## SoftCore Assembler (SoftAsm.py)
## William Diehl
## Version 2.1
## 5 Sep 2017

# Version 1.2 - added support for gf4 (gf(2^4) mod x^4 + x + 1) 2 operand multiplication
# Version 1.3 - added support for PRESENT 64-bit shift and permutation and LED 64-bit matrix multiplier column multiplication 
#	        added checking for syntax errors and unresolved or illegal references
# Version 2.0 - Compiles multiple source files simultaneously to produce a single object file.  Deconflicts between labels and directives across 
# 	        source files.  Requires that data segments in each source file be manually partitioned (i.e., does not relocate data addresses) 
# Version 2.1 - added support for adc (add with carry) s = a + b + c, where c is carry_in, which is set by previous ALU instructions

import time

# Required only for padding zeros for VHDL source code
import math

# Required to read arguments from command line
import sys
# get source file from argument list

# list of commands that execute in 1 clock cycle
cmd1list = ['lds', 'ldl', 'sts', 'stl', 'bcx', 'bnx', 'bzx', 'xor', 'trf', 'ret', 'str', 'lsr', 'inc', 'dec', 'not', 'nop', 'mov']

# list of commands that execute in 2 clock cycles
cmd2list = ['mvi', 'bci', 'bni', 'bzi', 'jmp', 'jsr', 'add', 'adc', 'sub', 'and', 'lor', 'ror', 'rol', 'srl', 'sll', 'gf2', 'gf3', 'gf4',
	   'prw', 'prr', 'prp', 'prs', 'mtw', 'mtr']

# check for a function in list of 1 clock cycle
def checkForOne(t):
	check1 = (t.find('lds')>-1)or(t.find('ldl')>-1)or(t.find('sts')>-1)or(t.find('stl')>-1)
	check1 = check1 or (t.find('bcx')>-1)or(t.find('bnx')>-1)or(t.find('bzx')>-1)or(t.find('xor')>-1)or(t.find('trf')>-1)or(t.find('ret')>-1)
	check1 = check1 or (t.find('str')>-1)or(t.find('lsr')>-1)or(t.find('inc')>-1)or(t.find('dec')>-1)
	check1 = check1 or (t.find('not')>-1)or(t.find('nop')>-1)or(t.find('mov')>-1)
	return check1

# check for a function in list of 2 clock cycles
def checkForTwo(t):
	check2 = (t.find('mvi')>-1)or(t.find('bci')>-1)or(t.find('bni')>-1)or(t.find('bzi')>-1)or(t.find('jmp')>-1)or(t.find('jsr')>-1)
	check2 = check2 or (t.find('add')>-1)or(t.find('sub')>-1)or(t.find('and')>-1)or(t.find('lor')>-1)or(t.find('gf2')>-1)or(t.find('adc')>-1)
	check2 = check2 or (t.find('ror')>-1)or(t.find('rol')>-1)or(t.find('srl')>-1)or(t.find('sll')>-1)or(t.find('gf3')>-1)or(t.find('gf4')>-1)
	check2 = check2 or (t.find('prw')>-1)or(t.find('prr')>-1)or(t.find('prp')>-1)or(t.find('prs')>-1)or(t.find('mtw')>-1)or(t.find('mtr')>-1)
	return check2

# return an 8-bit program word
def progword(opcode, src, dst):
	return returnHex(opcode) + returnHex((src * 4) + dst)


### string utility functions
hexlist = ['A', 'B', 'C', 'D', 'E', 'F']
declist = [10, 11, 12, 13, 14, 15]
numlist = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
hexmem = "0123456789abcdefABCDEF"

def returnHex(x):
	if (x < 10):
		s = str(x)
	else:
		s = hexlist[x-10]
	return s

# return a 2-digit hex string
def returnHex2(x):
	if (x < 16):
		s = '0' + returnHex(x)
	else:
		s = returnHex(x//16) + returnHex(x%16) 		
	return s

# return a 3-digit hex string
def returnHex3(x):
	if (x < 16):
		s = '00' + returnHex(x)
	else:
		if (x < 256):
			s = '0' + returnHex(x//16) + returnHex(x%16)
		else:
			y = x%256
			s = returnHex(x//256) + returnHex(y//16) + returnHex(y%16) 		
	return s

# returns an integer corresponding to a hex character
def returnHexNum(x):
	if (x == 'A'): y = 10
	if (x == 'B'): y = 11
	if (x == 'C'): y = 12
	if (x == 'D'): y = 13
	if (x == 'E'): y = 14
	if (x == 'F'): y = 15
	return y

# return an integer between 0 and 4095 from 3-digit hex string
def returnHex3Num(x):
	print ("x[0]: " + x[0])
	print ("x[1]: " + x[1])
	print ("x[2]: " + x[2])

	if (x[0] in hexlist):
		y = 256 * returnHexNum(x[0])
	else:
		y = 256 * int(x[0])

	if (x[1] in hexlist):
 		y = y + 16 * returnHexNum(x[1]) 
	else:
		y = y + 16 * int(x[1]) 
	
	if (x[2] in hexlist):
		y = y + returnHexNum(x[2])
	else:
		y = y + int(x[2])

	return y

# returns a block number between 0 and 3
def returnBlock(x):
	y = 0
	if (x > 2048):
		y = y + 2
		x = x - 2048
		if (x > 1024):
			y = y + 1
	return y

# takes an integer range 2^12-1 and returns least significant in range 0 - 2^10-1
def return10bit(x):
	if (x >= 2048):
		x = x - 2048
	if (x >= 1024):
		x = x - 1024
	return x

# takes an integer range 2^12-1 and returns least significant in range 0 - 2^10-1
def return8bit(x):
	if (x >= 2048):
		x = x - 2048
	if (x >= 1024):
		x = x - 1024
	if (x >= 512):
		x = x - 512
	if (x >= 256):
		x = x - 256	
	return x

### Syntax error detection

# Check Error 1 - check for "t" or "r" and proper operand for register
def checkError1(delim, op, linenum, PC, error):
	newerror = 0
	errstring = " in line " + str(linenum) + " and at PC=" + str(PC)
	if (delim == -1):
		newerror = 1
		errstring = "Syntax error" + errstring 
		print (errstring)
	if ((op<0) or (op>3)):
		newerror = 1
		errstring = "Syntax error - register operand not in range 0 to 3" + errstring 
		print (errstring)
	error = error + newerror
	return error	

# Check Error 2 - trailing fragement on line
def checkError2(t, linenum, PC, error):
	newerror = 0
	errstring = " in line " + str(linenum) + " and at PC=" + str(PC)
	if (len(t)!=0):
		newerror = 1
		errstring = "Syntax error" + errstring 
		print (errstring)
		error = error + newerror
	return error	

# Check Error 3 - unresolved or improper reference
def checkError3(t, linenum, PC, error):
	newerror = 0
	errstring = " in line " + str(linenum) + " and at PC=" + str(PC)
	if ((len(t)!=2) or (t[0] not in hexmem) or (t[1] not in hexmem)):
		newerror = 1
		errstring = "Syntax error - illegal immediate or reference" + errstring 
		print (errstring)
		error = error + newerror
	return error		

# Check Error 4 - unresolved or improper reference
def checkError4(t, linenum, PC, error):
	newerror = 0
	errstring = " in line " + str(linenum) + " and at PC=" + str(PC)
	if (t not in hexmem):
		newerror = 1
		errstring = "Syntax error - illegal immediate or reference" + errstring 
		print (errstring)
		error = error + newerror
	return error		

num_files = len(sys.argv)-1

# initialize tables
equlist = []
equvaluelist = []
lbllist = []
lblvaluelist = []

PC = 0
error = 0

startloc = []
endloc = []
maxargs = 4
for i in range(0,maxargs):
	startloc.append(0)
	endloc.append(0)

srcfile = []
for i in range (0, num_files):
	filename = str(sys.argv[i + 1]) 
	delim = filename.find('.txt')
	srcfile.append(filename[0:delim])
	
print ("Assembler started.  First pass - resolving references.")

for filenum in range (0, num_files):
	print ("Processing " + srcfile[filenum] + ".")
	openfile = open(srcfile[filenum] + '.txt', 'r')

	# Pass 1
	# First pass resolves references
	
	if (filenum==0):
		# Open a temporary file that will be used for the first pass. The temporary file remains as an artifact after completion.
		objfile = open(srcfile[0] + 'temp.txt','w')

	t = openfile.readline()
	while (t != ""):
		if (t.find('#')==0):
			print (t)
		else:		
			if (t.find('.start')>-1):
				if (t.find(' ')>-1):
					delim = t.find(' ')
					line1 = t[delim:len(t)]
					line2 = line1.lstrip()
					delim = line2.find('x')
					line3 = line2[delim+1:len(line2)]
					print (line3)
					startloc[filenum] = returnHex3Num(line3)
					PC = startloc[filenum]
				else:
					startloc[filenum] = PC			

			if (t.find('.equ')>-1):
				delim = t.find(' ')
				line1 = t[delim:len(t)]
				line2 = line1.lstrip()
				delim = line2.find(' ')
				label = srcfile[filenum] + line2[0:delim]
				equlist.append(label)
				line3 = line2[delim:len(line2)].lstrip()
				delim = line3.find('x')
				line4 = line3[delim+1:len(line3)]
				equvaluelist.append(line4)

			if (t.find('.lbl')>-1):
				delim = t.find(' ')
				line1 = t[delim:len(t)]
				line2 = line1.lstrip()
				delim = line2.find(' ')
				label = srcfile[filenum] + line2[0:delim]
				lbllist.append(label)
				lblvaluelist.append(PC)

			if (t.find('.end')>-1):
				endloc[filenum] = PC
				
			if (checkForOne(t)):
				objfile.write(srcfile[filenum] + ' ' + t)
				PC = PC + 1

			if (checkForTwo(t)):
				objfile.write(srcfile[filenum] + ' ' + t)
				PC = PC + 2

		t = openfile.readline()

	print ("First pass complete.")
	print (srcfile[filenum] + " start location: %X." % (startloc[filenum]))
	print (srcfile[filenum] + " end location: %X." % (endloc[filenum]))
	objfile.write('\n')
	openfile.close()

objfile.close()
highaddr = PC - 1
print ("Highest program address: %X." % (highaddr))
print ("Resolved the following references:")

for index in range(len(equlist)):
	print (equlist[index] + ' 0x' +  equvaluelist[index][0:len(equvaluelist[index])-1])

for index in range(len(lbllist)):
	print (lbllist[index] + ' 0x' +  returnHex3(lblvaluelist[index]))

print ("First pass complete.")

# Pass 2

print ("Start second pass.")

openfile = open(srcfile[0] + 'temp.txt', 'r')
obj = open(srcfile[0] + 'obj.txt','w')

# Assembly Header
localtime = time.asctime( time.localtime(time.time()) )
obj.write('-- Assembled by SoftAsm.py at ' + localtime + '\n')

for filenum in range (0, num_files):
	obj.write('-- ' + str(sys.argv[filenum + 1]) + ' start location: 0x' + returnHex3(startloc[filenum]) + '\n') 
	obj.write('-- ' + str(sys.argv[filenum + 1]) + ' end location: 0x' + returnHex3(endloc[filenum]) + '\n') 

obj.write('-- Highest program address: 0x' + returnHex3(highaddr) + '\n') 

for index in range(len(equlist)):
	obj.write('-- .equ '+ equlist[index] + ' 0x' + equvaluelist[index][0:len(equvaluelist[index])-1] + '\n')

for index in range(len(lbllist)):
	obj.write('-- .lbl '+ lbllist[index] + ' 0x' + returnHex3(lblvaluelist[index]) + '\n')

obj.write('\n')

PC = startloc[0]
linenum = 1
t = openfile.readline()
error = 0

while ((t != "") and(error==0)):

	instrfound = 0
	delim = t.find(' ')
	prefix = t[0:delim]
	t = t[delim:len(t)].lstrip()
	# echo command to command line interface
	print (t[0:len(t)-1])
	
	cmt = ' --' + 'PC=0x' + returnHex3(PC) + ' ' + t + '\n'

	for filenum in range (0, num_files):
		if (startloc[filenum] == PC):
			obj.write(' -------' + srcfile[filenum] + 'PC=0x' + returnHex3(PC) + '---- start -----\n') 	
		if (endloc[filenum] == PC):
			obj.write(' -------' + srcfile[filenum] + 'PC=0x' + returnHex3(PC) + '---- end -----\n')

	if (t.find('lds')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			opcode = 0x0
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",' + cmt[0:len(cmt)-1])
			PC = PC + 1

	if (t.find('ldl')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		if ((src != 0) and (src != 2)):
			error = 4
			print ("Illegal source register for LDL (permitted choices are r0 and r2)")
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			opcode = 0x1
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",' + cmt[0:len(cmt)-1])
			PC = PC + 1	
	
	if (t.find('sts')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			opcode = 0x2
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",' + cmt[0:len(cmt)-1])
			PC = PC + 1

	if (t.find('stl')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		if ((dst != 0) and (dst != 2)):
			error = 5
			print ("Illegal destination register for STL (permitted choices are r0 and r2)")		
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			opcode = 0x3
			obj.write('x\"')	
			obj.write(progword(opcode, src, dst))
			obj.write('\",' + cmt[0:len(cmt)-1])
			PC = PC + 1

	if (t.find('mov')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			opcode = 0x4
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",' + cmt[0:len(cmt)-1])
			PC = PC + 1
	
	if (t.find('mvi')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find(',')
		Im = t[0:delim]
		
		if ((prefix+Im) in equlist):
			Im = equvaluelist[equlist.index(prefix+Im)]
		
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			opcode = 0x5
			src = 0x0
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",' + cmt[0:len(cmt)-1] + 'x\"')
			if (Im.find('0x')>-1):
				obj.write(Im[2:4])
				error = checkError3(Im[2:4],linenum, PC, error)
			else:
				obj.write(Im[0:len(Im)-1])
				error = checkError3(Im[0:len(Im)-1],linenum, PC, error)
			obj.write('\",\n')	
			PC = PC + 2
			
	if (t.find('inc')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			src = 0x0
			opcode = 0x6
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",' + cmt[0:len(cmt)-1])
			PC = PC + 1

	if (t.find('dec')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			src = 0x1
			opcode = 0x6
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",' + cmt[0:len(cmt)-1])
			PC = PC + 1

	if (t.find('not')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			src = 0x2
			opcode = 0x6
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",' + cmt[0:len(cmt)-1])
			PC = PC + 1

	if (t.find('add')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			obj.write('x\"')
			obj.write('6C\",' + cmt[0:len(cmt)-1])
			opcode = 0x0
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",\n')
			PC = PC + 2

	if (t.find('sub')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			obj.write('x\"')
			obj.write('6C\",' + cmt[0:len(cmt)-1])
			opcode = 0x1
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",\n')
			PC = PC + 2

	if (t.find('and')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			obj.write('x\"')
			obj.write('6C\",' + cmt[0:len(cmt)-1])
			opcode = 0x2
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",\n')
			PC = PC + 2

	if (t.find('lor')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			obj.write('x\"')
			obj.write('6C\",' + cmt[0:len(cmt)-1])
			opcode = 0x3
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",\n')
			PC = PC + 2

	if (t.find('ror')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			obj.write('x\"')
			obj.write('6C\",' + cmt[0:len(cmt)-1])
			opcode = 0x4
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",\n')
			PC = PC + 2

	if (t.find('srl')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			obj.write('x\"')
			obj.write('6C\",' + cmt[0:len(cmt)-1])
			opcode = 0x5
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",\n')
			PC = PC + 2

	if (t.find('rol')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			obj.write('x\"')
			obj.write('6C\",' + cmt[0:len(cmt)-1])
			opcode = 0x6
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",\n')
			PC = PC + 2

	if (t.find('sll')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			obj.write('x\"')
			obj.write('6C\",' + cmt[0:len(cmt)-1])
			opcode = 0x7
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",\n')
			PC = PC + 2

	if (t.find('gf4')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			obj.write('x\"')
			obj.write('6C\",' + cmt[0:len(cmt)-1])
			opcode = 0x8
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",\n')
			PC = PC + 2

	if (t.find('adc')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			obj.write('x\"')
			obj.write('6C\",' + cmt[0:len(cmt)-1])
			opcode = 0x8
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",\n')
			PC = PC + 2

# Warning: gf4 and adc currently both assemble to same opcode - change is required to use both simultaneously

	if (t.find('gf2')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			obj.write('x\"')
			obj.write('6C\",' + cmt[0:len(cmt)-1])
			opcode = 0x9
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",\n')
			PC = PC + 2

	if (t.find('gf3')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			obj.write('x\"')
			obj.write('6C\",' + cmt[0:len(cmt)-1])
			opcode = 0xA
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",\n')
			PC = PC + 2

	if (t.find('prw')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			obj.write('x\"')
			obj.write('6C\",' + cmt[0:len(cmt)-1])
			opcode = 0xB
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",\n')
			PC = PC + 2

	if (t.find('prr')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			obj.write('x\"')
			obj.write('6C\",' + cmt[0:len(cmt)-1])
			opcode = 0xC
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",\n')
			PC = PC + 2

# Warning: mtw and prr currently both assemble to same opcode - change is required to use both simultaneously

	if (t.find('mtw')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			obj.write('x\"')
			obj.write('6C\",' + cmt[0:len(cmt)-1])
			opcode = 0xC
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",\n')
			PC = PC + 2

	if (t.find('prp')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			obj.write('x\"')
			obj.write('6C\",' + cmt[0:len(cmt)-1])
			opcode = 0xD
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",\n')
			PC = PC + 2

	if (t.find('prs')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			obj.write('x\"')
			obj.write('6C\",' + cmt[0:len(cmt)-1])
			opcode = 0xE
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",\n')
			PC = PC + 2

	if (t.find('mtr')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			obj.write('x\"')
			obj.write('6C\",' + cmt[0:len(cmt)-1])
			opcode = 0xF
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",\n')
			PC = PC + 2

	if (t.find('str')>-1):
		instrfound = 1
		t = t[t.find('str')+3:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		obj.write('x\"')
		obj.write('70\",' + cmt[0:len(cmt)-1])
		PC = PC + 1

	if (t.find('lsr')>-1):
		instrfound = 1
		t = t[t.find('lsr')+3:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		obj.write('x\"')
		obj.write('80\",' + cmt[0:len(cmt)-1])
		PC = PC + 1
	
	if (t.find('jsr')>-1):
		instrfound = 1
		delim = t.find(' ')
		Im = t[delim:len(t)-1].lstrip()
		if ((prefix+Im) in lbllist):
			i = lblvaluelist[lbllist.index(prefix+Im)]
			Im = returnHex3(i)

		i8 = return8bit(PC)
		if (i8 > 253):
			error = 2
			print ("Error: At PC 0x%X Jump target located on boundary of 256 byte block." % (PC))

		obj.write('x\"')
		obj.write('9' + Im[0] + '\",' + cmt[0:len(cmt)-1])
		error = checkError4(Im[0] , linenum, PC, error)
		obj.write('x\"')
		obj.write(Im[1:3] + '\",\n')
		error = checkError3(Im[1:3] , linenum, PC, error)
		PC = PC + 2

	if (t.find('ret')>-1):
		instrfound = 1
		t = t[t.find('ret')+3:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		obj.write('x\"')
		obj.write('A0\",' + cmt[0:len(cmt)-1])
		PC = PC + 1
	
	if (t.find('xor')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			opcode = 0xB
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",' + cmt[0:len(cmt)-1])
			PC = PC + 1

	if (t.find('trf')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('t')
		src = int(t[delim+1])
		error = checkError1(delim, src, linenum, PC, error)
		t = t[delim+1:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			opcode = 0xC
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",' + cmt[0:len(cmt)-1])
			PC = PC + 1

	if (t.find('jmp')>-1):
		instrfound = 1
		delim = t.find(' ')
		Im = t[delim:len(t)-1].lstrip()
		if ((prefix+Im) in lbllist):
			i = lblvaluelist[lbllist.index(prefix+Im)]
			Im = returnHex3(i)
		obj.write('x\"')
		obj.write('D' + Im[0] + '\",' + cmt[0:len(cmt)-1])
		error = checkError4(Im[0], linenum, PC, error)
		obj.write('x\"')
		obj.write(Im[1:3] + '\",\n')
		error = checkError3(Im[1:3], linenum, PC, error)
		PC = PC + 2

	if (t.find('bcx')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			src = 0x0
			opcode = 0xE
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",' + cmt[0:len(cmt)-1])
			PC = PC + 1

	if (t.find('bnx')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			src = 0x1
			opcode = 0xE
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",' + cmt[0:len(cmt)-1])
			PC = PC + 1

	if (t.find('bzx')>-1):
		instrfound = 1
		delim = t.find(' ')
		t = t[delim:len(t)].lstrip()
		delim = t.find('r')
		dst = int(t[delim+1])
		error = checkError1(delim, dst, linenum, PC, error)
		t = t[delim+2:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		if (error == 0):
			src = 0x2
			opcode = 0xE
			obj.write('x\"')
			obj.write(progword(opcode, src, dst))
			obj.write('\",' + cmt[0:len(cmt)-1])
			PC = PC + 1

	if (t.find('bci')>-1):
		instrfound = 1
		delim = t.find(' ')
		Im = t[delim:len(t)-1].lstrip()
		if ((prefix+Im) in lbllist):
			i = lblvaluelist[lbllist.index(prefix+Im)]
			iblock = returnBlock(i)
			i10 = return10bit(i)
			Im = returnHex3(i)
		PCblock = returnBlock(PC)
		PC10 = return10bit(PC)
		if ((iblock != PCblock) or (PC10 > 1021)):
			error = 1
			print (t)
			print ("Error: Branch target located outside of current 1024 byte block.")
		obj.write('x\"')
		obj.write('F'+ Im[0])
		obj.write('\",' + cmt[0:len(cmt)-1] + 'x\"')
		error = checkError4(Im[0], linenum, PC, error)
		obj.write(Im[1:3])
		error = checkError3(Im[1:3], linenum, PC, error)
		obj.write('\",\n')	
		PC = PC + 2

	if (t.find('bni')>-1):
		instrfound = 1
		delim = t.find(' ')
		Im = t[delim:len(t)-1].lstrip()
		if ((prefix+Im) in lbllist):
			i = lblvaluelist[lbllist.index(prefix+Im)]
			iblock = returnBlock(i)
			i10 = return10bit(i)
			i = i + 1024
			Im = returnHex3(i)
		PCblock = returnBlock(PC)
		PC10 = return10bit(PC)
		if ((iblock != PCblock) or (PC10 > 1021)):
			error = 1
			print (t)
			print ("Error: Branch target located outside of current 1024 byte block.")
		obj.write('x\"')
		obj.write('F'+ Im[0])
		error = checkError4(Im[0], linenum, PC, error)
		obj.write('\",' + cmt[0:len(cmt)-1] + 'x\"')
		obj.write(Im[1:3])
		error = checkError3(Im[1:3], linenum, PC, error)
		obj.write('\",\n')	
		PC = PC + 2
		
	if (t.find('bzi')>-1):
		instrfound = 1
		delim = t.find(' ')
		Im = t[delim:len(t)-1].lstrip()
		if ((prefix+Im) in lbllist):
			i = lblvaluelist[lbllist.index(prefix+Im)]
			iblock = returnBlock(i)
			i10 = return10bit(i)
			i = i + 2048
			Im = returnHex3(i)
		PCblock = returnBlock(PC)
		PC10 = return10bit(PC)
		if ((iblock != PCblock) or (PC10 > 1021)):
			error = 1
			print (t)
			print ("Error: Branch target located outside of current 1024 byte block.")
		obj.write('x\"')
		obj.write('F'+ Im[0])
		error = checkError4(Im[0], linenum, PC, error)
		obj.write('\",' + cmt[0:len(cmt)-1] + 'x\"')
		obj.write(Im[1:3])
		error = checkError3(Im[1:3], linenum, PC, error)
		obj.write('\",\n')	
		PC = PC + 2

	if (t.find('nop')>-1):
		instrfound = 1
		t = t[t.find('nop')+3:len(t)].lstrip()
		error = checkError2(t, linenum, PC, error)
		src = 0x0
		dst = 0x0
		opcode = 0x4
		obj.write('x\"')
		obj.write(progword(opcode, src, dst))
		obj.write('\",' + cmt[0:len(cmt)-1])
		PC = PC + 1

#	if (instrfound == 0):
#		insert future error checking routine if no valid instruction found

	t = openfile.readline()
	linenum = linenum + 1

openfile.close()

print ("Second pass complete.")
if (error == 0):

	# This section pads a VHDL Table with zeros fill 2^PMEM_SIZE
	PCsize = math.ceil(math.log10(PC)/0.30103)
	PCtop = math.pow(2,PCsize)
	paddedzeros = int(PCtop - PC)
	for i in range (1,paddedzeros):
		obj.write('x\"00\",\n')
	obj.write('x\"00\"\n')

	
	print ("Assembly complete. Object file is: " + srcfile[0] + "obj.txt.")

	for filenum in range (0, num_files):
		print (srcfile[filenum] + " start location: %X." % (startloc[filenum]))
		print (srcfile[filenum] + " end location: %X." %  (endloc[filenum]))

	PC = PC - 1
	print ("Highest program address: %X." % (PC))
	obj.close()
else:
	print ("Assembly failed due to errors.")

	# This section destroys the obj file because of errors to keep it from being used.
	#obj = open(srcfile[0] + 'obj.txt', 'w')
	#obj.write('\n')
	#obj.close()