# SoftCore
Soft Core Microprocessor
William Diehl
Version 1.3
01-30-2020

I. Contents:
1. Soft Core VHDL source files
2. AES encryption application source file and simulator files (data and table)
3. AES encryption object file
4. Assembler SoftAsm.py
5. Simulator SoftSim.py
6. Reference Manual

II. Limitations:
1. Assembler and Simulator verified in Windows 8; Does not function correctly in LINUX
2. Assembler (SoftAsm.py) and Simulator (SoftSim.py) compatible with Python 2.X
3. Assembler (SoftAsm_3_7.py) and Simulator (SoftSim_3_7.py) compatible with Python 3.X

III. Quick Start Guide:

1. Assembler
(a) Place SoftAsm.py (or SoftAsm_3_7.py) (assembler) and aesotf.txt (source file) in same directory with path to Python
(b) Execute assembler: python SoftAsm.py (or SoftAsm_3_7.py) aesotf.txt
(c) Object file is saved as aesotfobj.txt

2. Simulator
(a) Place SoftSim.py (or SoftSim_3_7.py) (simulator), aesotfobj.txt (object file), aesdataotf.txt (data file) and aestable.txt (table file) in same directory with path to Python
(b) Run simulator: python SoftSim.py (or SoftSim_3_7.py) aesotfobj.txt (Simulator command line interface is now active) 
(d) Add data file to data RAM: lmem aesdataotf.txt 0000
(e) To verify data entered into RAM, type: rmem 0000 0040 (dumps memory between addresses 0x0000 and 0x0040)
(f) Add table to Table ROM: ltab aestable.txt t0
(g) Run simulation using: run
(h) Upon completion, read data from RAM using: rmem 0000 0040.  Note result of encryption
(i) See reference manual for other simulator features

3. VHDL Simulation
(a) Start project in design environment, such as Xilinx ISE or Vivado
(b) Add all VHDL (.vhd) sources to project
(c) Run behavioral simulation using loader_tb.vhd as top module
(d) Add signals to simulation as desired.  For example, result of Soft Core simulation can be read on extdout interface once dataread is asserted at end of computation.
