# SoftSim.py
# William Diehl
# Updated 06/24/2018
# Version 2.2
# Summary of changes: 
# Version 2.0			
# 		      1) Adds support for object files compiled from multiple source files from SoftAsm v2.0
#		      2) Adds support setstart and setend commands
#		      3) Corrects certain issues with lmem and run commands 
# Version 2.1
#		      - adds support for adc (add with carry) s = a + b + cin
# Version 2.2
#		      - modifies the output format of status and log, including writes to SoftSimLog.txt 

import math

# Required to read arguments from command line
import sys
# get source file from argument list
sourcefile = str(sys.argv[1])
progfile = open(sourcefile, 'r')

### string utility functions
hexlist = ['A', 'B', 'C', 'D', 'E', 'F','a','b','c','d','e','f']
declist = [10, 11, 12, 13, 14, 15]
numlist = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

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
		s = returnHex(x/16) + returnHex(x%16) 		
	return s

# return a 3-digit hex string
def returnHex3(x):
	if (x < 16):
		s = '00' + returnHex(x)
	else:
		if (x < 256):
			s = '0' + returnHex(x/16) + returnHex(x%16)
		else:
			y = x%256
			s = returnHex(x/256) + returnHex(y/16) + returnHex(y%16) 		
	return s

# return a 4-digit hex string
def returnHex4(x):
	if (x < 16):
		s = '000' + returnHex(x)
	else:
		if (x < 256):
			s = '00' + returnHex(x/16) + returnHex(x%16)
		else:
			if (x < 4096):
				y = x%256
				s = '0' + returnHex(x/256) + returnHex(y/16) + returnHex(y%16)
			
			else:
				y = x%4096
				z = y%256
				s = returnHex(x/4096) + returnHex(y/256) + returnHex(z/16) + returnHex(z%16) 		
	return s


# returns an integer corresponding to a hex character
def returnHexNum(x):
	if ((x == 'A') or (x == 'a')): y = 10
	if ((x == 'B') or (x == 'b')): y = 11
	if ((x == 'C') or (x == 'c')): y = 12
	if ((x == 'D') or (x == 'd')): y = 13
	if ((x == 'E') or (x == 'e')): y = 14
	if ((x == 'F') or (x == 'f')): y = 15
	return y

# return an integer between 0 and 255 from 2-digit hex string
def returnHex2Num(x):

	if (x[0] in hexlist):
 		y = 16 * returnHexNum(x[0]) 
	else:
		y = 16 * int(x[0]) 
	
	if (x[1] in hexlist):
		y = y + returnHexNum(x[1])
	else:
		y = y + int(x[1])

	return y


# return an integer between 0 and 4095 from 3-digit hex string
def returnHex3Num(x):

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

# return an integer between 0 and 65535 from 4-digit hex string
def returnHex4Num(x):

	if (x[0] in hexlist):
		y = 4096 * returnHexNum(x[0])
	else:
		y = 4096 * int(x[0])

	if (x[1] in hexlist):
		y = y + 256 * returnHexNum(x[1])
	else:
		y = y + 256 * int(x[1])

	if (x[2] in hexlist):
 		y = y + 16 * returnHexNum(x[2]) 
	else:
		y = y + 16 * int(x[2]) 
	
	if (x[3] in hexlist):
		y = y + returnHexNum(x[3])
	else:
		y = y + int(x[3])

	return y


# status
def status(trace_flag):
	
	statusstr = "PC=0x" + returnHex3(PC) + " INSTR: 0x" + returnHex2(pmemcode[PC]) + " MNEM: " + pmemcom[PC] 
	statusstr = statusstr + " SP=0x" + returnHex4(SP) + "r3=0x" + returnHex2(reg[3]) + " r2=0x" + returnHex2(reg[2]) + " r1=0x" + returnHex2(reg[1]) + " r0=0x" + returnHex2(reg[0])
	statusstr = statusstr + " C=" + returnHex(Cflag) + " N=" + returnHex(Nflag) + " Z=" + returnHex(Zflag) + " Cin= " + returnHex(Cin) + " end=0x" + returnHex3(progend)
	if (breakflag):
		statusstr = statusstr + " break=0x" + returnHex3(progbreak)
	if (trace_flag):
        	print statusstr
	if (log):
		logfile.write(statusstr + '\n')
	return

# statistics
def statistics():

	if (totalcycles==0):
		currentIPC = float(0)
	else:
		currentIPC = float(totalinstr)/float(totalcycles)

	statisticsstr1 = "Instructions: " + str(totalinstr) + " Cycles: " + str(totalcycles) + " IPC: " + str(currentIPC)
	statisticsstr2 = ""
 	for i in range(0,maxinstr+1):
		statisticsstr2 = statisticsstr2 + instrmnemarray[i] + ": " + str(instrarray[i]) + "  "
	print statisticsstr1
	print statisticsstr2
	if (log):
		logfile.write(statisticsstr1 + '\n')
		logfile.write(statisticsstr2 + '\n')		

def prw(preg, operand, pword):
	initval = pword
	punpack = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
	for i in range (0,8):
		punpack[7-i]=initval/(256**(7-i))
		initval = initval % (256**(7-i))
	punpack[preg] = operand
	pword = 0L
	for i in range (0,8):
		pword = pword + punpack[7-i]*(256**(7-i))
	
	return pword

def prwext(preg, operand, pwordext):
	newpwordext = 0L
	punpack = [0x00, 0x00]
	punpack[1] =  pwordext / 256
	punpack[0] =  pwordext % 256
	if (preg==9):
		punpack[1] = operand
	else:
		if (preg==8):
			punpack[0] = operand
		else:
			print"Warning! Reference to preg out of range and undefined"
	newpwordext = punpack[1]*256 + punpack[0]
	return newpwordext

#used to set up the lower 64 bits of a left-circular shift on 80-bit word
def prs(pword, pwordext):

	a = 0L
	c = 0L
	newpword = 0L
	a = pword & 0x0000000000000007L
	c = pword >> 19
	a = a << 61
	pwordext = pwordext << 45
	newpword = a| pwordext | c
	return newpword

#used to set up the upper 16 bits of a left-circular shift on 80-bit word
def prsext(pword, pwordext):
	a = 0L
	newpwordext = 0L
	a = pword & 0x0000000000000007L
	pword = pword >> 3
	newpwordext = pword & 0x000000000000FFFFL
	return newpwordext

# used for instructions prr, prp, or prs (lower portion); depends on the supplied argument pword
def prr(preg, pword):
	punpack = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
	for i in range (0,8):
		punpack[7-i]=pword/(256**(7-i))
		pword = pword % (256**(7-i))
	return punpack[preg]

# used for instructions prs (upper portion)
def prrext(preg, pwordext):
	punpack = [0x00, 0x00]
	punpack[1] =  pwordext / 256
	punpack[0] =  pwordext % 256
	if ((preg < 8) or (preg>9)):
		print "Warning! Reference to preg out of range and undefined"
		return 0L
	else:
		return punpack[preg-8]

# 64-bit permutation
def prp(pword):
 
	pin = [0x0L, 0x0L, 0x0L, 0x0L]
	psum = [0x0L, 0x0L, 0x0L, 0x0L]
	mask1 = 0x1111111111111111L
	mask2 = 0x0000000000000001L

	for i in range (0,4):
		pin[i] = pword & mask1
		for j in range (0,16):
			if ((pin[i] & mask2) == 1):
				psum[i] = psum[i] + 2**j
			pin[i] = pin[i] >> 4
		pword = pword >> 1

	pperm = 0L
	for i in range (0,4):
		pperm = pperm + psum[i] * (65536**i)
	return pperm	

# 64-bit matrix multiplication column multiplication 
# writes value to register and computes column vector multiplication
# ma, mb, mc, md constant arrays are global variables
def mtw(mreg, operand, matsum):
	if (mreg == 0):
		matsum[0] = GF4(ma[0], operand)
		matsum[1] = GF4(mb[0], operand)
		matsum[2] = GF4(mc[0], operand)
		matsum[3] = GF4(md[0], operand)
	else:
		matsum[0] = matsum[0] ^ GF4(ma[mreg], operand)
		matsum[1] = matsum[1] ^ GF4(mb[mreg], operand)
		matsum[2] = matsum[2] ^ GF4(mc[mreg], operand)
		matsum[3] = matsum[3] ^ GF4(md[mreg], operand)
	return matsum

# 64-bit matrix multiplication column read
def mtr(mreg, matsum):
	return matsum[mreg]

def rol(dist, operand):
	int1 = operand << dist
	int2 = int1 & 0xFF00
	int3 = int2 >> 8
	int4 = int1 & 0x00FF
	return int4 | int3

def ror(dist, operand):
	int1 = operand << 8
	int2 = int1 >> dist
	int3 = int2 & 0x00FF
	int4 = (int2 & 0xFF00) >> 8
	return int4 | int3

def GF2(operand):
	int1 = operand << 1
	int2 = int1 & 0x00FF
	if (operand < 128):
		return int2
	else:
		return (int2 ^ 0x001b)

def GF3(operand):
	return (GF2(operand)^operand)

def GF4(op1, op2):
	return gf16[(op1 % 16) * 16 + (op2 % 16)]

## GF(2^4) mod x^4 + x + 1 multiplication tables

gf16 = (
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x1,0x2,0x3,0x4,0x5,0x6,0x7,0x8,0x9,0xA,0xB,0xC,0xD,0xE,0xF,
0x0,0x2,0x4,0x6,0x8,0xA,0xC,0xE,0x3,0x1,0x7,0x5,0xB,0x9,0xF,0xD,
0x0,0x3,0x6,0x5,0xC,0xF,0xA,0x9,0xB,0x8,0xD,0xE,0x7,0x4,0x1,0x2,
0x0,0x4,0x8,0xC,0x3,0x7,0xB,0xF,0x6,0x2,0xE,0xA,0x5,0x1,0xD,0x9,
0x0,0x5,0xA,0xF,0x7,0x2,0xD,0x8,0xE,0xB,0x4,0x1,0x9,0xC,0x3,0x6,
0x0,0x6,0xC,0xA,0xB,0xD,0x7,0x1,0x5,0x3,0x9,0xF,0xE,0x8,0x2,0x4,
0x0,0x7,0xE,0x9,0xF,0x8,0x1,0x6,0xD,0xA,0x3,0x4,0x2,0x5,0xC,0xB,
0x0,0x8,0x3,0xB,0x6,0xE,0x5,0xD,0xC,0x4,0xF,0x7,0xA,0x2,0x9,0x1,
0x0,0x9,0x1,0x8,0x2,0xB,0x3,0xA,0x4,0xD,0x5,0xC,0x6,0xF,0x7,0xE,
0x0,0xA,0x7,0xD,0xE,0x4,0x9,0x3,0xF,0x5,0x8,0x2,0x1,0xB,0x6,0xC,
0x0,0xB,0x5,0xE,0xA,0x1,0xF,0x4,0x7,0xC,0x2,0x9,0xD,0x6,0x8,0x3,
0x0,0xC,0xB,0x7,0x5,0x9,0xE,0x2,0xA,0x6,0x1,0xD,0xF,0x3,0x4,0x8,
0x0,0xD,0x9,0x4,0x1,0xC,0x8,0x5,0x2,0xF,0xB,0x6,0x3,0xE,0xA,0x7,
0x0,0xE,0xF,0x1,0xD,0x3,0x2,0xC,0x9,0x7,0x6,0x8,0x4,0xA,0xB,0x5,
0x0,0xF,0xD,0x2,0x9,0x6,0x4,0xB,0x1,0xE,0xC,0x3,0x8,0x7,0x5,0xA);

### 64-bit GF(2^4) matrix multiplication LED constants

ma = [0x4, 0x1, 0x2, 0x2]
mb = [0x8, 0x6, 0x5, 0x6]
mc = [0xB, 0xE, 0xA, 0x9]
md = [0x2, 0x2, 0xF, 0xB]

### 64-bit GF(2^4) matrix multiplication LED column multiplication result
	
ms = [0,0,0,0]

### loader generics
## dmemsize is exponent of number of bytes in dmem
## Example: 256 bytes of dmem -> 2^8 bytes -> set dmemsize=8
dmemsize = 8
dmemlimit = int(math.pow(2,dmemsize)-1)  

### define status variables
reg = [0,0,0,0]
SP = dmemlimit
PC = 0
Cflag = 0
Nflag = 0
Zflag = 0
Cin = 0
progend = 0
progbreak = 0
breakflag = False
firstcycle = True
dreg = 0
sreg = 0
error = False
trace = False
### permutation variables
### used only for permutation accelerator
pword = 0L
pwordext = 0L
pperm = 0L
prot61 = 0L
prot61ext = 0L
### end permutation accelerator variables

### define statistics variables
totalcycles = 0
totalinstr = 0
IPC = 0
instrarray = []
maxinstr = 39
for i in range(0,maxinstr+1):
	instrarray.append(0)
instrmnemarray = ['lds','ldl','sts','stl','mov','mvi','inc','dec','not','add','sub','and','lor','ror','slr',
                  'rol','sll','str','lsr','jsr','ret','xor','trf','jmp','bcx','bnx','bzx','bci','bni','bzi',
                  'gf2','gf3','gf4','prw','prr','prp','prs','mtw','mtr','adc']
progseq = []

### initiate error codes
errorarray = []
for i in range(0,10):
	errorarray.append("")

## define error codes

errorarray[0] = "Error! Object file has incorrect format"
errorarray[1] = "Error! Write index exceeds memory limits"
errorarray[2] = "Error! illegal memory address"
errorarray[3] = "Error! Illegal operand"
errorarray[4] = "Error! Stack overflow"
errorarray[5] = "Error! Stack underflow"
errorarray[6] = "Error! Value must be 0 or 1"
errorarray[7] = "Error! Unable to access file"

### initiate program memory
pmemcode = []
pmemcom = []
for i in range(0, 4096):
	pmemcode.append(0)
	pmemcom.append("")
		 
### initiate data memory
# change from i to 0 for working simulator
dmem = []
for i in range(0, 65536):
	dmem.append(0)

### initiate table memory
# change from i to 0 for working simulator
t0mem = []
t1mem = []
t2mem = []
t3mem = []
for i in range(0, 256):
	t0mem.append(0)
	t1mem.append(0)
	t2mem.append(0)
	t3mem.append(0)

logfile = open('SoftSimLog.txt','w')
log = False

nextline = progfile.readline()
nextline = progfile.readline()
if (nextline.find('tart location: 0x')>-1):
	delim = nextline.find(': 0x')
	startloc = returnHex3Num(nextline[delim+4:len(nextline)])
	PC = startloc
else:
	errorcode = 0	
	print errorarray[errorcode]

nextline = progfile.readline()
if (nextline.find('nd location: 0x')>-1):
	delim = nextline.find(': 0x')
	endloc = returnHex3Num(nextline[delim+4:len(nextline)])
else:
	errorcode = 0
	print errorarray[errorcode]

nextline = progfile.readline()
timeout = 0
maxtimeout = 12
while ((nextline.find('-- Highest program address: 0x')<0) and (timeout<maxtimeout)):
	timeout = timeout + 1
	nextline = progfile.readline()

if (nextline.find('-- Highest program address: 0x')>-1):
	delim = nextline.find('x')
	highprogaddr = returnHex3Num(nextline[delim+1:len(nextline)])
else:
	errorcode = 0
	print errorarray[errorcode]

nextline = progfile.readline()
while (nextline[0]!='x'):
	nextline= progfile.readline()

currentaddr = startloc
while (currentaddr <= highprogaddr):
	if (nextline[0]=='x'):
		delim = nextline.find('\"')
		str1 = nextline[delim+1:delim+3]
		opcode = returnHex2Num(str1)
		pmemcode[currentaddr] = opcode
		if (nextline.find('0x')>-1):
			delim = nextline.find('0x')
			mnem = nextline[delim+6:len(nextline)-1]
		else:
			mnem = pmemcom[currentaddr-1][0:3]+"2"+" NA"
		pmemcom[currentaddr] = mnem
		currentaddr = currentaddr + 1
	nextline = progfile.readline()

## display program after load
for i in range(0, highprogaddr+1):
	print returnHex2(pmemcode[i]) + "  " + pmemcom[i]
	
progfile.close()

print "Object file " + sourcefile + " loaded successfully."
print "Start location: " + returnHex3(startloc)
print "End location: " + returnHex3(endloc)
print "Highest program address: " + returnHex3(highprogaddr)
progend = endloc

str0 = raw_input("> ");
str1 = str0.lstrip();

while (str1 !="quit"):


	if (str1.find('rmem')>-1 or (str1.find('r')>-1 and len(str1)==1)):
		delim = str1.find(' ')
		str2 = str1[delim:len(str1)]
		startreadstr = str2[0:delim+1]
		startreadstr = startreadstr.lstrip()
		str3 = str2.lstrip()
		delim = str3.find(' ')
		endreadstr = str3[delim:len(str3)]
		endreadstr = endreadstr.lstrip()
		rmemstr = "rmem " + startreadstr + ' ' + endreadstr	
		print rmemstr
		if (log):
			logfile.write(rmemstr + '\n')

		startread = returnHex4Num(startreadstr)
		endread = returnHex4Num(endreadstr)
		startindex = startread/16
		offset = endread/16 - startread/16
		if (offset < 1):
			offset = 1
		dmemline = ""
		for i in range(0, offset):
			dmemline = returnHex4((startindex+i)*16) + ': '	
			for j in range(0,16):
				dmemline = dmemline + returnHex2(dmem[(startindex + i)*16 + j]) + " "
		
			print dmemline
			if (log):
				logfile.write(dmemline + '\n')
			dmemline = ""	
			
	if (str1.find('lmem')>-1):
		delim = str1.find(' ')
		str2 = str1[delim:len(str1)].lstrip()
		delim = str2.find(' ')
		writefilestr = str2[0:delim]
		writestartstr = str2[delim:len(str2)].lstrip()
		writestartindex = returnHex4Num(writestartstr)
		lmemstr = "lmem " + writefilestr + ' ' + writestartstr	
		print lmemstr
		if (log):
			logfile.write(lmemstr + '\n')
		try:
			memfile=open(writefilestr,'r')
			str0 = memfile.readline()
			while (str0.find('###EOF')<0):
				if (str0.find('#') <0):
					while (str0.find(' ')>-1):
						delim = str0.find(' ')
						writevalstr = str0[0:delim].lstrip()
						str0 = str0[delim:len(str0)].lstrip()
						if (writestartindex>dmemlimit):
							error = True
							errorcode = 1
							print errorarray[errorcode]
						else:
							dmem[writestartindex]=returnHex2Num(writevalstr)
							writestartindex = writestartindex + 1
						
					delim = str0.find('\n')
					writevalstr = str0[0:delim].lstrip()
					str0 = str0[delim:len(str0)].lstrip()
					if (writestartindex>dmemlimit):
						error = True
						errorcode = 1
						print errorarray[errorcode]
					else:
						dmem[writestartindex]=returnHex2Num(writevalstr)
						writestartindex = writestartindex + 1
					
				str0 = memfile.readline()
			memfile.close()
		except IOError:
			error = True
			errorcode = 7
			print errorarray[errorcode]

	if (str1.find('wmem')>-1 or (str1.find('w')>-1 and len(str1)==1)):
		delim = str1.find(' ')
		str2 = str1[delim:len(str1)].lstrip()
		delim = str2.find(' ')
		writeindexstr = str2[0:delim]
		writevalstr = str2[delim:len(str2)].lstrip()
	 	wmemstr = "wmem " + writeindexstr + ' ' + writevalstr	
		dmem[returnHex4Num(writeindexstr)]=returnHex2Num(writevalstr)
		print wmemstr
		if (log):
			logfile.write(wmemstr + '\n')
	

	if (str1.find('jump')>-1 or (str1.find('j')>-1 and len(str1)==1)):
		delim = str1.find(' ')
		writejumpstr = str1[delim:len(str1)].lstrip()
		jumpstr = "jump " + writejumpstr	
		print jumpstr
		if (log):
			logfile.write(jumpstr + '\n')
		PC = returnHex3Num(writejumpstr)

	if (str1.find('step')>-1 or (str1.find('s')>-1 and len(str1)==1)):
		print " execute step"
		if (log):
			logfile.write(" execute step" + '\n')
		# execute one clock cycle
		progseq.append(PC)

		if (firstcycle):
			msn = pmemcode[PC]/16   #most significant nibble
			lsn = pmemcode[PC]%16   #least significant nibble
			sreg = lsn/4
			dreg = lsn%4
			totalcycles = totalcycles + 1
			totalinstr = totalinstr + 1		

			if (msn == 0):	#lds [sreg],dreg
				reg[dreg]=dmem[reg[sreg]]
				PC = PC + 1
				instrarray[0] = instrarray[0]+1

			if (msn == 1): #ldl [sreg],dreg
				if (sreg == 0):
					srcaddr = reg[1]*256+reg[0]
					if (srcaddr > dmemlimit):
						error = True
						errorcode = 2
						print errorarray[errorcode]
					else:
						reg[dreg]=dmem[srcaddr]
				if (sreg == 2):
					srcaddr = reg[3]*256+reg[2]
					if (srcaddr > dmemlimit):
						error = True
						errorcode = 2
						print errorarray[errorcode]					
					else:
						reg[dreg]=dmem[srcaddr]
								
				if ((sreg==1) or (sreg==3)):
					error = True
					errorcode = 3
					print errorarray[errorcode]	
					
				PC = PC + 1
				instrarray[1] = instrarray[1]+1

			if (msn == 2): #sts sreg, [dreg]
				dmem[reg[dreg]] = reg[sreg]
				PC = PC + 1
				instrarray[2] = instrarray[2]+1

			if (msn == 3): #stl sreg,[dreg]
				if (dreg == 0):
					dstaddr = reg[1]*256+reg[0]
					if (dstaddr > dmemlimit):
						error = True
						errorcode = 2
						print errorarray[errorcode]
					else:
						dmem[dstaddr]=reg[sreg]

				if (dreg == 2):
					dstaddr = reg[3]*256+reg[2]
					if (dstaddr > dmemlimit):
						print "Error! illegal memory address"
					else:
						dmem[dstaddr]=reg[sreg]
			
				if ((dreg==1) or (dreg==3)):
					error = True
					errorcode = 3
					print errorarray[errorcode]
				PC = PC + 1
				instrarray[3] = instrarray[3]+1
				
			if (msn == 4):	# mov sreg, dreg
				reg[dreg]=reg[sreg]
				PC = PC + 1
				instrarray[4] = instrarray[4]+1
				
			if (msn == 5):	# mvi Im, dreg
				mnem = 'mvi'
				PC = PC + 1
				firstcycle = False
				instrarray[5] = instrarray[5]+1

			if (msn == 6): # ALU
				PC = PC + 1
				if (sreg == 0):  #inc dreg
					reg[dreg]=reg[dreg]+1
					if (reg[dreg]==256):
						Cflag=1
						Nflag=0
						reg[dreg]=0
					else:
						Cflag=0

					if (reg[dreg]==0):
						Zflag=1
					else:
						Zflag=0

					if (reg[dreg]>=128):
						Nflag=1
					else:
						Nflag=0
					instrarray[6] = instrarray[6]+1
					
				if (sreg == 1):  #dec dreg
					reg[dreg]=reg[dreg]-1
					if (reg[dreg]==0):
						Zflag=1
					else:			
						Zflag=0

					if (reg[dreg]==-1):
						Cflag=1
						Zflag=0
						reg[dreg]=255
						Nflag=1
					else:
						Cflag=0
					
					if (reg[dreg]>=128):
						Nflag=1
					else: 
						Nflag=0							

					instrarray[7] = instrarray[7]+1

				if (sreg == 2):  #not dreg
					reg[dreg]=~reg[dreg]
					reg[dreg]=reg[dreg]&0x00FF
					instrarray[8] = instrarray[8]+1

				if (sreg == 3):  # 2 cycle operation
					mnem = 'alu'
					firstcycle = False

			if (msn == 7): # str
				stword = Cflag
				stword = stword << 1
				stword = stword | Nflag
				stword = stword << 1
				stword = stword | Zflag
				dmem[SP] = stword
				if (SP == 0):
					print "Error! Stack overflow"
				SP = SP - 1
				PC = PC + 1
				instrarray[17] = instrarray[17]+1
			
			if (msn == 8): #lsr
				stword = dmem[SP+1]
				if (SP == dmemlimit):
					print "Error! Stack underflow"
				SP = SP + 1
				Zflag = stword & 0x0001
				Nflag = (stword >> 1)&0x0001
				Cflag = (stword >> 2)&0x0001
				instrarray[18] = instrarray[18]+1
				PC = PC + 1
	
			if (msn == 9): # jsr <addr>
				mnem = 'jsr'
				dmem[SP] = PC/256
				jumpaddrhigh = lsn
				if (SP == 0):
					error = True
					errorcode = 4
					print errorarray[errorcode]
				SP = SP - 1
				PC = PC + 1
				instrarray[19] = instrarray[19]+1
				firstcycle = False

			if (msn == 10): # ret
				mnem = 'ret'
				retaddrlow = dmem[SP+1]
				if (SP == dmemlimit):
					error = True
					errorcode = 5
					print errorarray[errorcode]
				SP = SP + 1
				instrarray[20] = instrarray[20]+1
				firstcycle = False

			if (msn == 11): # xor sreg, dreg
				reg[dreg]=reg[dreg]^reg[sreg]
				PC = PC + 1
				instrarray[21] = instrarray[21]+1

			if (msn == 12): # trf <op>,dreg
				if (sreg == 0):
					reg[dreg]=t0mem[reg[dreg]]
				if (sreg == 1):
					reg[dreg]=t1mem[reg[dreg]]
				if (sreg == 2):
					reg[dreg]=t2mem[reg[dreg]]
				if (sreg == 3):
					reg[dreg]=t3mem[reg[dreg]]
				PC = PC + 1
				instrarray[22] = instrarray[22]+1

			if (msn == 13): # jmp <addr>
				mnem = 'jmp'
				jumpaddrhigh = lsn
				PC = PC + 1
				firstcycle = False
				instrarray[23] = instrarray[23]+1

			if (msn == 14): # bxx [dreg]
				if (sreg == 0): # bcx
					if (Cflag==1):
						PC = (PC/256)*256+reg[dreg]
						Cflag=0
						Nflag=0
						Zflag=0
					else:
						PC = PC + 1
					instrarray[24] = instrarray[24]+1
		
				if (sreg == 1): # bnx
					if (Nflag==1):
						PC = (PC/256)*256+reg[dreg]
						Cflag=0
						Nflag=0
						Zflag=0
					else:
						PC = PC + 1	
					instrarray[25] = instrarray[25]+1
	
				if (sreg == 2): # bzx
					if (Zflag==1):
						PC = (PC/256)*256+reg[dreg]
						Cflag=0
						Nflag=0
						Zflag=0
					else:
						PC = PC + 1	
					instrarray[26] = instrarray[26]+1

			if (msn == 15): # bxi <addr>
				if (sreg == 0): # bcx
					mnem = 'bci'
					instrarray[27] = instrarray[27]+1

				if (sreg == 1): # bni
					mnem = 'bni'
					instrarray[28] = instrarray[28]+1

				if (sreg == 2): # bzi
					mnem= 'bzi'
					instrarray[29] = instrarray[29]+1
					
				jumpaddrhigh = (PC/1024)*1024+dreg
				PC = PC + 1
				firstcycle = False

		else:
			totalcycles = totalcycles + 1
			firstcycle = True
			if (mnem == 'mvi'):
				imval = pmemcode[PC]
				reg[dreg]=imval
				PC = PC + 1

			if (mnem == 'alu'):
				aluop = pmemcode[PC]/16
				lsn = pmemcode[PC]%16
				sreg = lsn/4
				dreg = lsn%4
				PC = PC + 1
				if (aluop == 0): # add sreg, dreg
					reg[dreg] = reg[sreg] + reg[dreg]
					if (reg[dreg]>=256):
						Cflag = 1
					else:
						Cflag = 0	
					reg[dreg] = reg[dreg] & 0x00FF
					if (reg[dreg]>=128):
						Nflag = 1
					else:
						Nflag = 0
					if (reg[dreg]==0):
						Zflag = 1
					else:
						Zflag = 0
					instrarray[9] = instrarray[9]+1

				if (aluop == 1): # sub sreg, dreg
					if (reg[dreg]>reg[sreg]):
						Cflag = 1
					else:
						Cflag = 0
					reg[dreg] = reg[sreg] - reg[dreg]
					if (reg[dreg]<0):
						Nflag = 1
					else:
						Nflag = 0
					reg[dreg] = reg[dreg] & 0x00FF
					if (reg[dreg]==0):
						Zflag = 1
					else:
						Zflag = 0
					instrarray[10] = instrarray[10]+1
			
				if (aluop == 2): # and sreg, dreg
					reg[dreg] = reg[sreg] & reg[dreg]
					instrarray[11] = instrarray[11]+1
					
				if (aluop == 3): # lor sreg, dreg
					reg[dreg] = reg[sreg] | reg[dreg]
					instrarray[12] = instrarray[12]+1

				if (aluop == 4): # ror <sreg=dist>, dreg
					reg[dreg] = ror(reg[sreg],reg[dreg])
					instrarray[13] = instrarray[13]+1

				if (aluop == 5): # slr sreg, dreg
					reg[dreg] = reg[dreg]>>reg[sreg]
					instrarray[14] = instrarray[14]+1
					# set c, n, z flag

				if (aluop == 6): #rol <sreg=dist>,dreg				 
					reg[dreg] = rol(reg[sreg],reg[dreg])
					instrarray[15] = instrarray[15]+1

				if (aluop == 7): # sll sreg, dreg
					reg[dreg] = reg[dreg] << reg[sreg]
					reg[dreg] = reg[dreg] & 0x00FF
					# set c, n, z flag
					instrarray[16] = instrarray[16]+1
				
# Uncomment if using gf4
#				if (aluop == 8): # gf4 sreg, dreg
#					reg[dreg] = gf16[(reg[sreg] % 16)*16 + (reg[dreg] % 16)]
#					# set flags
#					instrarray[32] = instrarray[32]+1

# Comment out the below if using gf4
				if (aluop == 8): # adc sreg, dreg
					reg[dreg] = reg[sreg] + reg[dreg] + Cin
					if (reg[dreg]>=256):
						Cflag = 1
						Cin = 1
					else:
						Cflag = 0
						Cin = 0	
					reg[dreg] = reg[dreg] & 0x00FF
					if (reg[dreg]>=128):
						Nflag = 1
					else:
						Nflag = 0
					if (reg[dreg]==0):
						Zflag = 1
					else:
						Zflag = 0
					instrarray[9] = instrarray[9]+1

				if (aluop == 9): # gf2 sreg, dreg
					reg[dreg] = GF2(reg[sreg])
					# set flags
					instrarray[30] = instrarray[30]+1
						
				if (aluop == 10): # gf3 sreg, dreg
					reg[dreg] = GF3(reg[sreg])
					# set flags
					instrarray[31] = instrarray[31]+1

				if (aluop == 11): # prw sreg, dreg
					# range of preg can only be 0..9
					preg = reg[sreg] & 0x000F
					if (preg > 7):
						pwordext = prwext(preg, reg[dreg], pwordext)
						prot61 = prs(pword, pwordext)
						prot61ext = prsext(pword, pwordext)
					else:
						pword = prw(preg,reg[dreg],pword)
						prot61 = prs(pword, pwordext)
						prot61ext = prsext(pword, pwordext)
					pperm = prp(pword)
					instrarray[33] = instrarray[33]+1

# removed to insert mtw and mtr

#				if (aluop == 12): # prr sreg, dreg
#					# range of preg can only be 0..7
#					preg = reg[sreg] & 0x0007
#					reg[dreg] = prr(preg, pword)									
#					instrarray[34] = instrarray[34]+1

				if (aluop == 12): #mtw sreg, dreg
					# range of mreg can only be 0..3
					mreg = reg[sreg] & 0x0003
					ms = mtw(mreg, reg[dreg], ms)
					instrarray[37] = instrarray[37] + 1
								
				if (aluop == 13): # prp sreg, dreg
					# range of preg can only be 0..7
					preg = reg[sreg] & 0x0007
					reg[dreg] = prr(preg, pperm)									
					instrarray[35] = instrarray[35]+1

				if (aluop == 14): # prs sreg, dreg
					# range of preg can be 0..9
					preg = reg[sreg] & 0x000F
					if (preg > 7):
						reg[dreg] = prrext(preg, prot61ext)
					else:
						reg[dreg] = prr(preg, prot61)
					instrarray[36] = instrarray[36] + 1

				if (aluop == 15): # mtr sreg, dreg
					# range of mreg can be 0..3
					mreg = reg[sreg] & 0x0003
					reg[dreg] = mtr(mreg, ms)
					instrarray[38] = instrarray[38] + 1

			if (mnem == 'jsr'):
				dmem[SP] = PC%256 + 1
				if (SP == 0):
					error = True
					errorcode = 4
					print errorarray[errorcode]

				SP = SP - 1
				PC = jumpaddrhigh * 256 + pmemcode[PC]	
			

			if (mnem == 'ret'):
				retaddrhigh = dmem[SP+1]
				if (SP == dmemlimit):
					error = True
					errorcode = 5
					print errorarray[errorcode]

				SP = SP + 1
				PC = retaddrhigh * 256 + retaddrlow

			if (mnem == 'jmp'):
				PC = jumpaddrhigh*256 + pmemcode[PC]
							
			if (mnem == 'bci'):
				if (Cflag == 1):
					Cflag=0
					Nflag=0
					Zflag=0
					PC = jumpaddrhigh *256 + pmemcode[PC]
				else:
					PC = PC + 1

			if (mnem == 'bni'):
				if (Nflag == 1):
					Cflag=0
					Nflag=0
					Zflag=0
					PC = jumpaddrhigh *256 + pmemcode[PC]
				else:
					PC = PC + 1

			if (mnem == 'bzi'):
				if (Zflag == 1):
					Cflag=0
					Nflag=0
					Zflag=0
					PC = jumpaddrhigh *256 + pmemcode[PC]
				else:
					PC = PC + 1


		if (PC == endloc):
			print"Warning! End of Program"
		if (PC >= highprogaddr):
			print"Warning! PC is at or above high program address"
		if (PC < startloc):
			print"Warning! PC is below start program address"
		status(True)		

	if ((str1.find('run')>-1) or (str1.find('cont')>-1)):
		if (str1.find('run')>-1):
			print " execute run"
			if (log):
				logfile.write(" execute run" + '\n')
			# run until end point, break point, error, or high program address

			PC = startloc
			reg = [0,0,0,0]
			Cflag = 0
			Nflag = 0
			Zflag = 0
			error = False
		else:
			error = False
			print " execute continue"
			if (log):
				logfile.write(" execute continue" + '\n')
			# run until end point, break point, error, or high program address
				
	
		status(trace) # call status for first command at initialization
		while ((PC!=endloc) and (PC<=highprogaddr) and (error==False) and ((breakflag==False) or (PC!=progbreak))):
	
                        progseq.append(PC)
			if (firstcycle):
				msn = pmemcode[PC]/16   #most significant nibble
				lsn = pmemcode[PC]%16   #least significant nibble
				sreg = lsn/4
				dreg = lsn%4		
				totalcycles = totalcycles + 1
				totalinstr = totalinstr + 1		
				
				if (msn == 0):	#lds [sreg],dreg
					reg[dreg]=dmem[reg[sreg]]
					PC = PC + 1
					instrarray[0]=instrarray[0]+1

				if (msn == 1): #ldl [sreg],dreg
					if (sreg == 0):
						srcaddr = reg[1]*256+reg[0]
						if (srcaddr > dmemlimit):
							error = True
							errorcode = 2
							print errorarray[errorcode]
						else:
							reg[dreg]=dmem[srcaddr]
					if (sreg == 2):
						srcaddr = reg[3]*256+reg[2]
						if (srcaddr > dmemlimit):
							error = True
							errorcode = 2
							print errorarray[errorcode]					
						else:
							reg[dreg]=dmem[srcaddr]
								
					if ((sreg==1) or (sreg==3)):
						error = True
						errorcode = 3
						print errorarray[errorcode]	
					
					PC = PC + 1
					instrarray[1]=instrarray[1]+1

				if (msn == 2): #sts sreg, [dreg]
					dmem[reg[dreg]] = reg[sreg]
					PC = PC + 1
					instrarray[2]=instrarray[2]+1

				if (msn == 3): #stl sreg,[dreg]
					if (dreg == 0):
						dstaddr = reg[1]*256+reg[0]
						if (dstaddr > dmemlimit):
							error = True
							errorcode = 2
							print errorarray[errorcode]
						else:
							dmem[dstaddr]=reg[sreg]

					if (dreg == 2):
						dstaddr = reg[3]*256+reg[2]
						if (dstaddr > dmemlimit):
							print "Error! illegal memory address"
						else:
							dmem[dstaddr]=reg[sreg]
			
					if ((dreg==1) or (dreg==3)):
						error = True
						errorcode = 3
						print errorarray[errorcode]
					PC = PC + 1
					instrarray[3]=instrarray[3]+1
							
				if (msn == 4):	# mov sreg, dreg
					reg[dreg]=reg[sreg]
					PC = PC + 1
					instrarray[4]=instrarray[4]+1
				
				if (msn == 5):	# mvi Im, dreg
					mnem = 'mvi'
					PC = PC + 1
					firstcycle = False
					instrarray[5]=instrarray[5]+1

				if (msn == 6): # ALU
					PC = PC + 1
					if (sreg == 0):  #inc dreg
						reg[dreg]=reg[dreg]+1
						if (reg[dreg]==256):
							Cflag=1
							Nflag=0
							reg[dreg]=0
						else:
							Cflag=0

						if (reg[dreg]==0):
							Zflag=1
						else:
							Zflag=0

						if (reg[dreg]>=128):
							Nflag=1
						else:
							Nflag=0
						instrarray[6]=instrarray[6]+1

					if (sreg == 1):  #dec dreg
						reg[dreg]=reg[dreg]-1
						if (reg[dreg]==0):
							Zflag=1
						else:			
							Zflag=0

						if (reg[dreg]==-1):
							Cflag=1
							Zflag=0
							reg[dreg]=255
							Nflag=1
						else:
							Cflag=0
					
						if (reg[dreg]>=128):
							Nflag=1
						else: 
							Nflag=0							
						instrarray[7]=instrarray[7]+1

					if (sreg == 2):  #not dreg
						reg[dreg]=~reg[dreg]
						reg[dreg]=reg[dreg]&0x00FF
						instrarray[8]=instrarray[8]+1

					if (sreg == 3):  # 2 cycle operation
						mnem = 'alu'
						firstcycle = False

				if (msn == 7): # str
					stword = Cflag
					stword = stword << 1
					stword = stword | Nflag
					stword = stword << 1
					stword = stword | Zflag
					dmem[SP] = stword
					if (SP == 0):
						print "Error! Stack overflow"
					SP = SP - 1
					PC = PC + 1
					instrarray[17]=instrarray[17]+1
			
				if (msn == 8): #lsr
					stword = dmem[SP+1]
					if (SP == dmemlimit):
						print "Error! Stack underflow"
					SP = SP + 1
					Zflag = stword & 0x0001
					Nflag = (stword >> 1)&0x0001
					Cflag = (stword >> 2)&0x0001
					PC = PC + 1
					instrarray[18]=instrarray[18]+1
	
				if (msn == 9): # jsr <addr>
					mnem = 'jsr'
					dmem[SP] = PC/256
					jumpaddrhigh = lsn
					if (SP == 0):
						error = True
						errorcode = 4
						print errorarray[errorcode]
					SP = SP - 1
					PC = PC + 1
					firstcycle = False
					instrarray[19]=instrarray[19]+1

				if (msn == 10): # ret
					mnem = 'ret'
					retaddrlow = dmem[SP+1]
					if (SP == dmemlimit):
						error = True
						errorcode = 5
						print errorarray[errorcode]
					SP = SP + 1
					firstcycle = False
					instrarray[20]=instrarray[20]+1

				if (msn == 11): # xor sreg, dreg
					reg[dreg]=reg[dreg]^reg[sreg]
					PC = PC + 1
					instrarray[21]=instrarray[21]+1

				if (msn == 12): # trf <op>,dreg
					if (sreg == 0):
						reg[dreg]=t0mem[reg[dreg]]
					if (sreg == 1):
						reg[dreg]=t1mem[reg[dreg]]
					if (sreg == 2):
						reg[dreg]=t2mem[reg[dreg]]
					if (sreg == 3):
						reg[dreg]=t3mem[reg[dreg]]
					PC = PC + 1
					instrarray[22]=instrarray[22]+1

				if (msn == 13): # jmp <addr>
					mnem = 'jmp'
					jumpaddrhigh = lsn
					PC = PC + 1
					firstcycle = False
					instrarray[23]=instrarray[23]+1

				if (msn == 14): # bxx [dreg]
					if (sreg == 0): # bcx
						if (Cflag==1):
							PC = (PC/256)*256+reg[dreg]
							Cflag=0
							Nflag=0
							Zflag=0
						else:
							PC = PC + 1
						instrarray[24]=instrarray[24]+1

					if (sreg == 1): # bnx
						if (Nflag==1):
							PC = (PC/256)*256+reg[dreg]
							Cflag=0
							Nflag=0
							Zflag=0
						else:
							PC = PC + 1	
						instrarray[25]=instrarray[25]+1
					
					if (sreg == 2): # bzx
						if (Zflag==1):
							PC = (PC/256)*256+reg[dreg]
							Cflag=0
							Nflag=0
							Zflag=0
						else:
							PC = PC + 1	
						instrarray[26]=instrarray[26]+1

				if (msn == 15): # bxi <addr>
					if (sreg == 0): # bcx
						mnem = 'bci'
						instrarray[27]=instrarray[27]+1

					if (sreg == 1): # bni
						mnem = 'bni'
						instrarray[28]=instrarray[28]+1

					if (sreg == 2): # bzi
						mnem= 'bzi'
						instrarray[29]=instrarray[29]+1

					jumpaddrhigh = (PC/1024)*1024+dreg
					PC = PC + 1
					firstcycle = False

			else:
				totalcycles = totalcycles + 1
				firstcycle = True
				if (mnem == 'mvi'):
					imval = pmemcode[PC]
					reg[dreg]=imval
					PC = PC + 1

				if (mnem == 'alu'):
					aluop = pmemcode[PC]/16
					lsn = pmemcode[PC]%16
					sreg = lsn/4
					dreg = lsn%4
					PC = PC + 1
					if (aluop == 0): # add sreg, dreg
						reg[dreg] = reg[sreg] + reg[dreg]
						if (reg[dreg]>=256):
							Cflag = 1
						else:
							Cflag = 0	
						reg[dreg] = reg[dreg] & 0x00FF
						if (reg[dreg]>=128):
							Nflag = 1
						else:
							Nflag = 0
						if (reg[dreg]==0):
							Zflag = 1
						else:
							Zflag = 0

						instrarray[9]=instrarray[9]+1

					if (aluop == 1): # sub sreg, dreg
						if (reg[dreg]>reg[sreg]):
							Cflag = 1
						else:
							Cflag = 0
						reg[dreg] = reg[sreg] - reg[dreg]
						if (reg[dreg]<0):
							Nflag = 1
						else:
							Nflag = 0
						reg[dreg] = reg[dreg] & 0x00FF
						if (reg[dreg]==0):
							Zflag = 1
						else:
							Zflag = 0
						instrarray[10]=instrarray[10]+1
			
					if (aluop == 2): # and sreg, dreg
						reg[dreg] = reg[sreg] & reg[dreg]
						instrarray[11]=instrarray[11]+1

					if (aluop == 3): # lor sreg, dreg
						reg[dreg] = reg[sreg] | reg[dreg]
						instrarray[12]=instrarray[12]+1
				
					if (aluop == 4): # ror <sreg=dist>, dreg
						reg[dreg] = ror(reg[sreg],reg[dreg])
						instrarray[13]=instrarray[13]+1

					if (aluop == 5): # slr sreg, dreg
						reg[dreg] = reg[dreg]>>reg[sreg]
						# set c, n, z flag
						instrarray[14]=instrarray[14]+1

					if (aluop == 6): #rol <sreg=dist>,dreg				 
						reg[dreg] = rol(reg[sreg],reg[dreg])
						instrarray[15]=instrarray[15]+1

					if (aluop == 7): # sll sreg, dreg
						reg[dreg] = reg[dreg] << reg[sreg]
						reg[dreg] = reg[dreg] & 0x00FF
						# set c, n, z flag
						instrarray[16]=instrarray[16]+1

# Uncomment if using gf4 and comment adc below
#					if (aluop == 8): # gf4 sreg, dreg
#						reg[dreg] = gf16[(reg[sreg] % 16)*16 + (reg[dreg] % 16)]
#						# set flags
#						instrarray[32] = instrarray[32]+1

#Comment out if using gf4; cannot be used at same time
					if (aluop == 8): # adc sreg, dreg
						reg[dreg] = reg[sreg] + reg[dreg] + Cin
						if (reg[dreg]>=256):
							Cflag = 1
							Cin = 1
						else:
							Cflag = 0
							Cin = 0	
						reg[dreg] = reg[dreg] & 0x00FF
						if (reg[dreg]>=128):
							Nflag = 1
						else:
							Nflag = 0
						if (reg[dreg]==0):
							Zflag = 1
						else:
							Zflag = 0

						instrarray[9]=instrarray[9]+1
					

					if (aluop == 9): # gf2 sreg, dreg
						reg[dreg] = GF2(reg[sreg])
						# set flags
						instrarray[30]=instrarray[30]+1
			
					if (aluop == 10): # gf3 sreg, dreg
						reg[dreg] = GF3(reg[sreg])
						# set flags
						instrarray[31]=instrarray[31]+1

					if (aluop == 11): # prw sreg, dreg
						# range of preg can only be 0..9
						preg = reg[sreg] & 0x000F
						if (preg > 7):
							pwordext = prwext(preg, reg[dreg], pwordext)
							prot61 = prs(pword, pwordext)
							prot61ext = prsext(pword, pwordext)
						else:
							pword = prw(preg,reg[dreg],pword)
							prot61 = prs(pword, pwordext)
							prot61ext = prsext(pword, pwordext)
						pperm = prp(pword)
						instrarray[33] = instrarray[33]+1

#					if (aluop == 12): # prr sreg, dreg
#						# range of preg can only be 0..7
#						preg = reg[sreg] & 0x0007
#						reg[dreg] = prr(preg, pword)									
#						instrarray[34] = instrarray[34]+1

					if (aluop == 12): #mtw sreg, dreg
						# range of mreg can only be 0..3
						mreg = reg[sreg] & 0x0003
						ms = mtw(mreg, reg[dreg], ms)
						instrarray[37] = instrarray[37] + 1

					if (aluop == 13): # prp sreg, dreg
						# range of preg can only be 0..7
						preg = reg[sreg] & 0x0007
						reg[dreg] = prr(preg, pperm)									
						instrarray[35] = instrarray[35]+1

					if (aluop == 14): # prs sreg, dreg
						# range of preg can be 0..9
						preg = reg[sreg] & 0x000F
						if (preg > 7):
							reg[dreg] = prrext(preg, prot61ext)
						else:
							reg[dreg] = prr(preg, prot61)
						instrarray[36] = instrarray[36] + 1

					if (aluop == 15): # mtr sreg, dreg
						# range of mreg can be 0..3
						mreg = reg[sreg] & 0x0003
						reg[dreg] = mtr(mreg, ms)
						instrarray[38] = instrarray[38] + 1
								
				if (mnem == 'jsr'):
					dmem[SP] = PC%256 + 1
					if (SP == 0):
						error = True
						errorcode = 4
						print errorarray[errorcode]

					SP = SP - 1
					PC = jumpaddrhigh * 256 + pmemcode[PC]				

				if (mnem == 'ret'):
					retaddrhigh = dmem[SP+1]
					if (SP == dmemlimit):
						error = True
						errorcode = 5
						print errorarray[errorcode]

					SP = SP + 1
					PC = retaddrhigh * 256 + retaddrlow

				if (mnem == 'jmp'):
					PC = jumpaddrhigh*256 + pmemcode[PC]
							
				if (mnem == 'bci'):
					if (Cflag == 1):
						Cflag=0
						Nflag=0
						Zflag=0
						PC = jumpaddrhigh *256 + pmemcode[PC]
					else:
						PC = PC + 1

				if (mnem == 'bni'):
					if (Nflag == 1):
						Cflag=0
						Nflag=0
						Zflag=0
						PC = jumpaddrhigh *256 + pmemcode[PC]
					else:
						PC = PC + 1

				if (mnem == 'bzi'):
					if (Zflag == 1):
						Cflag=0
						Nflag=0
						Zflag=0
						PC = jumpaddrhigh *256 + pmemcode[PC]
					else:
						PC = PC + 1

                        status(trace)

		if (PC == endloc):
			print "Program end point"
		if (breakflag and (PC==progbreak)):
			print "Program break point"
		if (error):
			print"At PC = 0x" + returnHex3(PC)
			print errorarray[errorcode]		

	if (str1.find('setbreak')>-1):
		delim = str1.find(' ')
		writebreakstr = str1[delim:len(str1)].lstrip()
		breakstr = "setbreak " + writebreakstr	
		print breakstr
		if (log):
			logfile.write(breakstr + '\n')
		progbreak = returnHex3Num(writebreakstr)
		breakflag = True	

	if (str1.find('setend')>-1):
		delim = str1.find(' ')
		writeendstr = str1[delim:len(str1)].lstrip()
		endstr = "setend " + writeendstr	
		print endstr
		if (log):
			logfile.write(endstr + '\n')
		progend = returnHex3Num(writeendstr)
		endloc = progend

	if (str1.find('setstart')>-1):
		delim = str1.find(' ')
		writestartstr = str1[delim:len(str1)].lstrip()
		startstr = "setstart " + writestartstr	
		print startstr
		if (log):
			logfile.write(startstr + '\n')
		startloc = returnHex3Num(writestartstr)

	if (str1.find('clrbreak')>-1):
		breakstr = "clrbreak " + writebreakstr	
		print breakstr
		if (log):
			logfile.write(breakstr + '\n')
		breakflag = False		
	
	if (str1.find('wreg')>-1):
		delim = str1.find(' ')
		str2 = str1[delim:len(str1)].lstrip()
		delim = str2.find(' ')
		writeregstr = str2[0:delim]
		writevalstr = str2[delim:len(str2)].lstrip()
		wregstr = "wreg " + writeregstr + ' ' + writevalstr	
		print wregstr
		if (log):
			logfile.write(wregstr + '\n')
		if (writeregstr == 'r0'):
			reg[0] = returnHex2Num(writevalstr)
		if (writeregstr == 'r1'):
			reg[1] = returnHex2Num(writevalstr)
		if (writeregstr == 'r2'):
			reg[2] = returnHex2Num(writevalstr)
		if (writeregstr == 'r3'):
			reg[3] = returnHex2Num(writevalstr)

	if (str1.find('rtab')>-1):
	
		delim = str1.find(' ')
		str2 = str1[delim:len(str1)]
		tabreadstr = str2[0:delim+1].lstrip()
		rtabstr = "rtab " + tabreadstr	
		print rtabstr
		if (log):
			logfile.write(rtabstr + '\n')
		
		tabline = ""
		for i in range(0, 16):
			tabline = returnHex2(i*16) + ': '	
			for j in range(0,16):
				tabval = 0
				if (tabreadstr=='t0'):
					tabval=t0mem[i*16 + j]
				if (tabreadstr=='t1'):
					tabval=t1mem[i*16 + j]
				if (tabreadstr=='t2'):
					tabval=t2mem[i*16 + j]
				if (tabreadstr=='t3'):
					tabval=t3mem[i*16 + j]

				tabline = tabline + returnHex2(tabval) + " "
		
			print tabline
			if (log):
				logfile.write(tabline + '\n')
			tabline = ""

	if (str1.find('reset')>-1):
		PC = 0
		SP = dmemlimit
		reg = [0,0,0,0]
		Cflag = 0
		Nflag = 0
		Zflag = 0
		Cin = 0
		breakflag = False
		totalcycles = 0
		totalinstr = 0
		for i in range (0,maxinstr+1):
			instrarray[i]=0
		print "reset"
		if (log):
			logfile.write('reset' + '\n')
		status(True)
	
	if (str1.find('ltab')>-1):

		delim = str1.find(' ')
		str2 = str1[delim:len(str1)].lstrip()
		delim = str2.find(' ')
		writefilestr = str2[0:delim]
		writetabstr = str2[delim:len(str2)].lstrip()
		writestartindex = 0
		ltabstr = "ltab " + writefilestr + ' ' + writetabstr	
		print ltabstr
		if (log):
			logfile.write(ltabstr + '\n')
		
		try:
			tabfile=open(writefilestr,'r')
			str0 = tabfile.readline()
			while (str0 != "###EOF"):
				if (str0.find('#') <0):
					while (str0.find(' ')>-1):
						delim = str0.find(' ')
						writevalstr = str0[0:delim].lstrip()
						str0 = str0[delim:len(str0)].lstrip()
						if (writestartindex>dmemlimit):
							error = True	
							errorcode = 1										
							print errorarray[errorcode]
						else:
							if (writetabstr == 't0'):
								t0mem[writestartindex]=returnHex2Num(writevalstr)
							if (writetabstr == 't1'):
								t1mem[writestartindex]=returnHex2Num(writevalstr)
							if (writetabstr == 't2'):
								t2mem[writestartindex]=returnHex2Num(writevalstr)
							if (writetabstr == 't3'):
								t3mem[writestartindex]=returnHex2Num(writevalstr)

						writestartindex = writestartindex + 1

					delim = str0.find('\n')
					writevalstr = str0[0:delim].lstrip()
					str0 = str0[delim:len(str0)].lstrip()
					if (writestartindex>dmemlimit):
						error = True	
						errorcode = 1										
						print errorarray[errorcode]
					else:
						if (writetabstr == 't0'):
							t0mem[writestartindex]=returnHex2Num(writevalstr)
						if (writetabstr == 't1'):
							t1mem[writestartindex]=returnHex2Num(writevalstr)
						if (writetabstr == 't2'):
							t2mem[writestartindex]=returnHex2Num(writevalstr)
						if (writetabstr == 't3'):
							t3mem[writestartindex]=returnHex2Num(writevalstr)

					writestartindex = writestartindex + 1

				str0 = tabfile.readline()
			tabfile.close()
		except IOError:
			error = True
			errorcode = 7
			print errorarray[errorcode]

	if (str1.find('status')>-1 or (str1.find('st')>-1 and len(str1)==2)):
		status(True)

	if (str1.find('dumpstats')>-1):
		instrfile = open('SoftSimStats.txt','w')
		for i in range(0,maxinstr):
			instrfile.write(instrmnemarray[i]+","+ str(instrarray[i])+"\n")
		instrfile.write(instrmnemarray[maxinstr]+","+str(instrarray[maxinstr]))
		instrfile.close()

		progseqfile = open('SoftSimProgSeq.txt','w')
		for i in range(0,len(progseq)-1):
			progseqfile.write(str(progseq[i]) + ",")
		progseqfile.write(str(progseq[len(progseq)-1]))
		progseqfile.close()

	
	if (str1.find('statistics')>-1 or str1.find('stats')>-1):
		statistics()
	
	if (str1.find('logon')>-1):
		log = True
		print " execute logon"

	if (str1.find('logoff')>-1):
		log = False
		print " execute logoff"

	if (str1.find('traceon')>-1):
		trace = True
		print " execute traceon"

	if (str1.find('traceoff')>-1):
		trace = False
		print " execute traceoff"

	if (str1.find('setflag')>-1):

		delim = str1.find(' ')
		str2 = str1[delim:len(str1)].lstrip()
		delim = str2.find(' ')
		writeflagstr = str2[0:delim]
		writevalstr = str2[delim:len(str2)].lstrip()
		setflagstr = "setflag " + writeflagstr + ' ' + writevalstr	
		print setflagstr
		if (log):
			logfile.write(setflagstr + '\n')
		if (writevalstr == '0' or writevalstr == '1'):
			if (writeflagstr == 'C'):
				Cflag = int(writevalstr)
			if (writeflagstr == 'N'):
				Nflag = int(writevalstr)
			if (writeflagstr == 'Z'):
				Zflag = int(writevalstr)
			if (writeflagstr == 'Cin'):
				Cin = int(writevalstr)
		else:
			error = True
			errorcode = 6
			print errorarray[errorcode]

	if (str1.find('wsp')>-1):
		delim = str1.find(' ')
		writespstr = str1[delim:len(str1)].lstrip()
		wspstr = "wsp " + writespstr	
		print wspstr
		if (log):
			logfile.write(wspstr + '\n')
		SP = returnHex4Num(writespstr)

	str0 = raw_input("> ");
	str1 = str0.lstrip();
	if (log):
		logfile.write(str1+'\n')
	
logfile.close()