-- progloader
-- AES Round keys computed on the fly
-- Set Generic PMEM => 9

LIBRARY ieee;
USE ieee.std_logic_1164.all;
USE ieee.numeric_std.all;

ENTITY progloader IS
	generic(
		LOADER_SIZE : integer:= 8
		);

	PORT(
		addr: IN STD_LOGIC_VECTOR(LOADER_SIZE - 1 DOWNTO 0);
		dout: OUT STD_LOGIC_VECTOR(7 DOWNTO 0)
	);

END progloader;

ARCHITECTURE dataflow OF progloader IS

SIGNAL index: INTEGER RANGE 0 TO 2**LOADER_SIZE - 1;
TYPE vector_array IS ARRAY (0 to 2**LOADER_SIZE-1) OF STD_LOGIC_VECTOR(7 DOWNTO 0);
CONSTANT memory : vector_array := 
	(


-- Assembled by SoftAsm.py at Sat Dec 31 17:13:04 2016
-- Start location: 0x000
-- End location: 0x01D
-- Highest program address: 0x18C
-- .equ key0 0x00
-- .equ gptr 0x0D
-- .equ gptrp1 0x0E
-- .equ rcptr 0x2F
-- .equ gmem 0x2A
-- .equ op1ptr 0x30
-- .equ op2ptr 0x31
-- .equ keyptr 0x32
-- .equ wrptr 0x33
-- .equ cntr 0x34
-- .equ rndcnt 0x35
-- .equ tmp1 0x2E
-- .equ tmp2 0x36
-- .equ tmp3 0x37
-- .equ ptext 0x10
-- .equ s1 0x11
-- .equ s2 0x12
-- .equ s3 0x13
-- .equ s5 0x15
-- .equ s6 0x16
-- .equ s7 0x17
-- .equ s9 0x19
-- .equ s10 0x1A
-- .equ s11 0x1B
-- .equ s13 0x1D
-- .equ s14 0x1E
-- .equ s15 0x1F
-- .lbl lp4 0x004
-- .lbl lp4dne 0x017
-- .lbl RndKyOtf 0x01E
-- .lbl wrd1 0x07E
-- .lbl wrdxr 0x094
-- .lbl wrdxrloop 0x09A
-- .lbl wrdxrdne 0x0B0
-- .lbl AdRndKy 0x0B1
-- .lbl lp1 0x0BA
-- .lbl lp1end 0x0C9
-- .lbl Sbytes 0x0CA
-- .lbl lp2 0x0CE
-- .lbl lp2end 0x0D7
-- .lbl ShftRw 0x0D8
-- .lbl MxCl 0x117
-- .lbl lp3 0x121
-- .lbl lp3end 0x18C

x"90", --PC=0x000 jsr AdRndKy
x"B1",
x"90", --PC=0x002 jsr RndKyOtf
x"1E",
x"90", --PC=0x004 jsr Sbytes
x"CA",
x"90", --PC=0x006 jsr ShftRw
x"D8",
x"91", --PC=0x008 jsr MxCl
x"17",
x"90", --PC=0x00A jsr AdRndKy
x"B1",
x"90", --PC=0x00C jsr RndKyOtf
x"1E",
x"50", --PC=0x00E mvi rndcnt, r0
x"35",
x"01", --PC=0x010 lds r0, r1
x"65", --PC=0x011 dec r1
x"24", --PC=0x012 sts r1, r0
x"F8", --PC=0x013 bzi lp4dne
x"17",
x"D0", --PC=0x015 jmp lp4
x"04",
x"90", --PC=0x017 jsr Sbytes
x"CA",
x"90", --PC=0x019 jsr ShftRw
x"D8",
x"90", --PC=0x01B jsr AdRndKy
x"B1",
 -------PC=0x01D---- end -----
x"40", --PC=0x01D nop
x"50", --PC=0x01E mvi keyptr, r0
x"32",
x"51", --PC=0x020 mvi 0x00, r1
x"00",
x"24", --PC=0x022 sts r1, r0
x"50", --PC=0x023 mvi wrptr, r0
x"33",
x"24", --PC=0x025 sts r1, r0
x"50", --PC=0x026 mvi gptr, r0
x"0D",
x"51", --PC=0x028 mvi rcptr, r1
x"2F",
x"02", --PC=0x02A lds r0, r2
x"C2", --PC=0x02B trf t0, r2
x"07", --PC=0x02C lds r1, r3
x"0C", --PC=0x02D lds r3, r0
x"B2", --PC=0x02E xor r0, r2
x"63", --PC=0x02F inc r3
x"2D", --PC=0x030 sts r3,r1
x"51", --PC=0x031 mvi gmem, r1
x"2A",
x"29", --PC=0x033 sts r2, r1
x"61", --PC=0x034 inc r1
x"50", --PC=0x035 mvi gptrp1, r0
x"0E",
x"02", --PC=0x037 lds r0, r2
x"C2", --PC=0x038 trf t0, r2
x"29", --PC=0x039 sts r2, r1
x"61", --PC=0x03A inc r1
x"60", --PC=0x03B inc r0
x"02", --PC=0x03C lds r0, r2
x"C2", --PC=0x03D trf t0, r2
x"29", --PC=0x03E sts r2, r1
x"61", --PC=0x03F inc r1
x"64", --PC=0x040 dec r0
x"64", --PC=0x041 dec r0
x"64", --PC=0x042 dec r0
x"02", --PC=0x043 lds r0, r2
x"C2", --PC=0x044 trf t0, r2
x"29", --PC=0x045 sts r2, r1
x"52", --PC=0x046 mvi keyptr, r2
x"32",
x"08", --PC=0x048 lds r2, r0
x"51", --PC=0x049 mvi op1ptr, r1
x"30",
x"21", --PC=0x04B sts r0, r1
x"60", --PC=0x04C inc r0
x"60", --PC=0x04D inc r0
x"60", --PC=0x04E inc r0
x"60", --PC=0x04F inc r0
x"22", --PC=0x050 sts r0, r2
x"50", --PC=0x051 mvi gmem, r0
x"2A",
x"51", --PC=0x053 mvi op2ptr, r1
x"31",
x"21", --PC=0x055 sts r0, r1
x"50", --PC=0x056 mvi 0x04, r0
x"04",
x"51", --PC=0x058 mvi cntr, r1
x"34",
x"21", --PC=0x05A sts r0, r1
x"90", --PC=0x05B jsr wrdxr
x"94",
x"50", --PC=0x05D mvi 0x04, r0
x"04",
x"51", --PC=0x05F mvi cntr, r1
x"34",
x"21", --PC=0x061 sts r0, r1
x"90", --PC=0x062 jsr wrd1
x"7E",
x"90", --PC=0x064 jsr wrdxr
x"94",
x"50", --PC=0x066 mvi 0x04, r0
x"04",
x"51", --PC=0x068 mvi cntr, r1
x"34",
x"21", --PC=0x06A sts r0, r1
x"90", --PC=0x06B jsr wrd1
x"7E",
x"90", --PC=0x06D jsr wrdxr
x"94",
x"50", --PC=0x06F mvi 0x04, r0
x"04",
x"51", --PC=0x071 mvi cntr, r1
x"34",
x"21", --PC=0x073 sts r0, r1
x"90", --PC=0x074 jsr wrd1
x"7E",
x"90", --PC=0x076 jsr wrdxr
x"94",
x"50", --PC=0x078 mvi 0x04, r0
x"04",
x"51", --PC=0x07A mvi cntr, r1
x"34",
x"21", --PC=0x07C sts r0, r1
x"A0", --PC=0x07D ret
x"52", --PC=0x07E mvi keyptr, r2
x"32",
x"08", --PC=0x080 lds r2, r0
x"51", --PC=0x081 mvi op1ptr, r1
x"30",
x"21", --PC=0x083 sts r0, r1
x"60", --PC=0x084 inc r0
x"60", --PC=0x085 inc r0
x"60", --PC=0x086 inc r0
x"60", --PC=0x087 inc r0
x"22", --PC=0x088 sts r0, r2
x"50", --PC=0x089 mvi wrptr, r0
x"33",
x"00", --PC=0x08B lds r0, r0
x"64", --PC=0x08C dec r0
x"64", --PC=0x08D dec r0
x"64", --PC=0x08E dec r0
x"64", --PC=0x08F dec r0
x"51", --PC=0x090 mvi op2ptr, r1
x"31",
x"21", --PC=0x092 sts r0, r1
x"A0", --PC=0x093 ret
x"52", --PC=0x094 mvi op2ptr, r2
x"31",
x"0A", --PC=0x096 lds r2, r2
x"53", --PC=0x097 mvi op1ptr, r3
x"30",
x"0F", --PC=0x099 lds r3, r3
x"0C", --PC=0x09A lds r3, r0
x"63", --PC=0x09B inc r3
x"09", --PC=0x09C lds r2, r1
x"62", --PC=0x09D inc r2
x"B1", --PC=0x09E xor r0, r1
x"50", --PC=0x09F mvi wrptr, r0
x"33",
x"00", --PC=0x0A1 lds r0, r0
x"24", --PC=0x0A2 sts r1, r0
x"60", --PC=0x0A3 inc r0
x"51", --PC=0x0A4 mvi wrptr, r1
x"33",
x"21", --PC=0x0A6 sts r0, r1
x"50", --PC=0x0A7 mvi cntr, r0
x"34",
x"01", --PC=0x0A9 lds r0, r1
x"65", --PC=0x0AA dec r1
x"24", --PC=0x0AB sts r1, r0
x"F8", --PC=0x0AC bzi wrdxrdne
x"B0",
x"D0", --PC=0x0AE jmp wrdxrloop
x"9A",
x"A0", --PC=0x0B0 ret
x"50", --PC=0x0B1 mvi ptext, r0
x"10",
x"51", --PC=0x0B3 mvi key0, r1
x"00",
x"52", --PC=0x0B5 mvi cntr, r2
x"34",
x"53", --PC=0x0B7 mvi 0x10, r3
x"10",
x"2E", --PC=0x0B9 sts r3, r2
x"02", --PC=0x0BA lds r0, r2
x"07", --PC=0x0BB lds r1, r3
x"BB", --PC=0x0BC xor r2, r3
x"2C", --PC=0x0BD sts r3, r0
x"60", --PC=0x0BE inc r0
x"61", --PC=0x0BF inc r1
x"52", --PC=0x0C0 mvi cntr, r2
x"34",
x"0B", --PC=0x0C2 lds r2, r3
x"67", --PC=0x0C3 dec r3
x"2E", --PC=0x0C4 sts r3, r2
x"F8", --PC=0x0C5 bzi lp1end
x"C9",
x"D0", --PC=0x0C7 jmp lp1
x"BA",
x"A0", --PC=0x0C9 ret
x"50", --PC=0x0CA mvi ptext, r0
x"10",
x"52", --PC=0x0CC mvi 0x10, r2
x"10",
x"01", --PC=0x0CE lds r0, r1
x"C1", --PC=0x0CF trf t0, r1
x"24", --PC=0x0D0 sts r1, r0
x"60", --PC=0x0D1 inc r0
x"66", --PC=0x0D2 dec r2
x"F8", --PC=0x0D3 bzi lp2end
x"D7",
x"D0", --PC=0x0D5 jmp lp2
x"CE",
x"A0", --PC=0x0D7 ret
x"50", --PC=0x0D8 mvi tmp1, r0
x"2E",
x"51", --PC=0x0DA mvi s1, r1
x"11",
x"06", --PC=0x0DC lds r1, r2
x"28", --PC=0x0DD sts r2, r0
x"53", --PC=0x0DE mvi s5, r3
x"15",
x"0E", --PC=0x0E0 lds r3, r2
x"29", --PC=0x0E1 sts r2, r1
x"50", --PC=0x0E2 mvi s9, r0
x"19",
x"02", --PC=0x0E4 lds r0, r2
x"2B", --PC=0x0E5 sts r2, r3
x"53", --PC=0x0E6 mvi s13, r3
x"1D",
x"0E", --PC=0x0E8 lds r3, r2
x"28", --PC=0x0E9 sts r2, r0
x"50", --PC=0x0EA mvi tmp1, r0
x"2E",
x"02", --PC=0x0EC lds r0, r2
x"2B", --PC=0x0ED sts r2, r3
x"50", --PC=0x0EE mvi s2, r0
x"12",
x"51", --PC=0x0F0 mvi s10, r1
x"1A",
x"02", --PC=0x0F2 lds r0, r2
x"07", --PC=0x0F3 lds r1, r3
x"29", --PC=0x0F4 sts r2, r1
x"2C", --PC=0x0F5 sts r3, r0
x"50", --PC=0x0F6 mvi s6, r0
x"16",
x"51", --PC=0x0F8 mvi s14, r1
x"1E",
x"02", --PC=0x0FA lds r0, r2
x"07", --PC=0x0FB lds r1, r3
x"29", --PC=0x0FC sts r2, r1
x"2C", --PC=0x0FD sts r3, r0
x"53", --PC=0x0FE mvi tmp1, r3
x"2E",
x"50", --PC=0x100 mvi s15, r0
x"1F",
x"01", --PC=0x102 lds r0, r1
x"27", --PC=0x103 sts r1, r3
x"51", --PC=0x104 mvi s11, r1
x"1B",
x"06", --PC=0x106 lds r1, r2
x"28", --PC=0x107 sts r2, r0
x"53", --PC=0x108 mvi s7, r3
x"17",
x"0E", --PC=0x10A lds r3, r2
x"29", --PC=0x10B sts r2, r1
x"51", --PC=0x10C mvi s3, r1
x"13",
x"04", --PC=0x10E lds r1, r0
x"23", --PC=0x10F sts r0, r3
x"50", --PC=0x110 mvi tmp1, r0
x"2E",
x"00", --PC=0x112 lds r0, r0
x"51", --PC=0x113 mvi s3, r1
x"13",
x"21", --PC=0x115 sts r0, r1
x"A0", --PC=0x116 ret
x"50", --PC=0x117 mvi cntr, r0
x"34",
x"51", --PC=0x119 mvi 0x04, r1
x"04",
x"24", --PC=0x11B sts r1, r0
x"50", --PC=0x11C mvi ptext, r0
x"10",
x"51", --PC=0x11E mvi op1ptr, r1
x"30",
x"21", --PC=0x120 sts r0, r1
x"01", --PC=0x121 lds r0, r1
x"6C", --PC=0x122 gf2 r1, r1
x"95",
x"60", --PC=0x124 inc r0
x"02", --PC=0x125 lds r0, r2
x"6C", --PC=0x126 gf3 r2, r2
x"AA",
x"B6", --PC=0x128 xor r1, r2
x"60", --PC=0x129 inc r0
x"01", --PC=0x12A lds r0, r1
x"B6", --PC=0x12B xor r1, r2
x"60", --PC=0x12C inc r0
x"01", --PC=0x12D lds r0, r1
x"B6", --PC=0x12E xor r1, r2
x"53", --PC=0x12F mvi tmp1, r3
x"2E",
x"2B", --PC=0x131 sts r2, r3
x"50", --PC=0x132 mvi op1ptr, r0
x"30",
x"00", --PC=0x134 lds r0, r0
x"01", --PC=0x135 lds r0, r1
x"60", --PC=0x136 inc r0
x"02", --PC=0x137 lds r0, r2
x"6C", --PC=0x138 gf2 r2, r2
x"9A",
x"B6", --PC=0x13A xor r1, r2
x"60", --PC=0x13B inc r0
x"01", --PC=0x13C lds r0, r1
x"6C", --PC=0x13D gf3 r1, r1
x"A5",
x"B6", --PC=0x13F xor r1, r2
x"60", --PC=0x140 inc r0
x"01", --PC=0x141 lds r0, r1
x"B6", --PC=0x142 xor r1, r2
x"53", --PC=0x143 mvi tmp2, r3
x"36",
x"2B", --PC=0x145 sts r2, r3
x"50", --PC=0x146 mvi op1ptr, r0
x"30",
x"00", --PC=0x148 lds r0, r0
x"01", --PC=0x149 lds r0, r1
x"60", --PC=0x14A inc r0
x"02", --PC=0x14B lds r0, r2
x"B6", --PC=0x14C xor r1, r2
x"60", --PC=0x14D inc r0
x"01", --PC=0x14E lds r0, r1
x"6C", --PC=0x14F gf2 r1, r1
x"95",
x"B6", --PC=0x151 xor r1, r2
x"60", --PC=0x152 inc r0
x"01", --PC=0x153 lds r0, r1
x"6C", --PC=0x154 gf3 r1, r1
x"A5",
x"B6", --PC=0x156 xor r1, r2
x"53", --PC=0x157 mvi tmp3, r3
x"37",
x"2B", --PC=0x159 sts r2, r3
x"50", --PC=0x15A mvi op1ptr, r0
x"30",
x"00", --PC=0x15C lds r0, r0
x"01", --PC=0x15D lds r0, r1
x"60", --PC=0x15E inc r0
x"02", --PC=0x15F lds r0, r2
x"6C", --PC=0x160 gf3 r1, r1
x"A5",
x"B6", --PC=0x162 xor r1, r2
x"60", --PC=0x163 inc r0
x"01", --PC=0x164 lds r0, r1
x"B6", --PC=0x165 xor r1, r2
x"60", --PC=0x166 inc r0
x"01", --PC=0x167 lds r0, r1
x"6C", --PC=0x168 gf2 r1, r1
x"95",
x"B6", --PC=0x16A xor r1, r2
x"28", --PC=0x16B sts r2, r0
x"64", --PC=0x16C dec r0
x"52", --PC=0x16D mvi tmp3, r2
x"37",
x"0B", --PC=0x16F lds r2, r3
x"2C", --PC=0x170 sts r3, r0
x"64", --PC=0x171 dec r0
x"52", --PC=0x172 mvi tmp2, r2
x"36",
x"0B", --PC=0x174 lds r2, r3
x"2C", --PC=0x175 sts r3, r0
x"64", --PC=0x176 dec r0
x"52", --PC=0x177 mvi tmp1, r2
x"2E",
x"0B", --PC=0x179 lds r2, r3
x"2C", --PC=0x17A sts r3, r0
x"53", --PC=0x17B mvi cntr, r3
x"34",
x"0E", --PC=0x17D lds r3, r2
x"66", --PC=0x17E dec r2
x"2B", --PC=0x17F sts r2, r3
x"F9", --PC=0x180 bzi lp3end
x"8C",
x"51", --PC=0x182 mvi op1ptr, r1
x"30",
x"04", --PC=0x184 lds r1, r0
x"60", --PC=0x185 inc r0
x"60", --PC=0x186 inc r0
x"60", --PC=0x187 inc r0
x"60", --PC=0x188 inc r0
x"21", --PC=0x189 sts r0, r1
x"D1", --PC=0x18A jmp lp3
x"21",
x"A0", --PC=0x18C ret
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00",
x"00"





);

BEGIN

	index <= to_integer(unsigned(addr));
	dout <= memory(index);

END dataflow;
