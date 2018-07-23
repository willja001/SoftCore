-- dataloader
-- AES Round Keys computed on the fly
-- Set DMEM Generic to 6

LIBRARY ieee;
USE ieee.std_logic_1164.all;
USE ieee.numeric_std.all;

ENTITY dataloader IS
	generic(
		LOADER_SIZE : integer:= 8
		);

	PORT(
		addr: IN STD_LOGIC_VECTOR(LOADER_SIZE - 1 DOWNTO 0);
		dout: OUT STD_LOGIC_VECTOR(7 DOWNTO 0)
	);

END dataloader;

ARCHITECTURE dataflow OF dataloader IS

SIGNAL index: INTEGER RANGE 0 TO 2**LOADER_SIZE - 1;
TYPE vector_array IS ARRAY (0 to 2**LOADER_SIZE-1) OF STD_LOGIC_VECTOR(7 DOWNTO 0);
CONSTANT memory : vector_array := 
	(

-- memory map
-- 0x00 - 0x0F original secret key
-- secret key overwritten during round key scheduling

x"00",x"00",x"00",x"00",x"00",x"00",x"00",x"00",
x"00",x"00",x"00",x"00",x"00",x"00",x"00",x"00",
		
--0x10 - 0x1F - 16 bytes plaintext (Note: Ciphertext overwrites plaintext in this version)

x"00",x"00",x"00",x"00",x"00",x"00",x"00",x"00",
x"00",x"00",x"00",x"00",x"00",x"00",x"00",x"00",

--0x20 - 0x29 (32 - 41) Round Constants 1 to 10
--0x2A - 0x2D (42 - 45) g function memory (4 bytes)
--0x2E (46) tmp1
--0x2F (47) rcptr - pointer to current round constant

x"01",x"02",x"04",x"08",x"10",x"20",x"40",x"80",
x"1B",x"36",x"00",x"00",x"00",x"00",x"0D",x"20",

--0x30 (48) op1ptr - pointer to wrdxr operand 1 
--0x31 (49) op2ptr - pointer to wrdxr operand 2
--0x32 (50) keyptr - pointer to next subkey (k0 - k43)
--0x33 (51) wrptr - pointer to next wrdxr write
--0x34 (42) cntr - wrdxr counter
--0x35 (53) rndcnt - round counter (10 rounds)
--0x36 - 0x37 tmp2 - 3
--0x39 - 0x3F - reserved for stack

x"00",x"00",x"00",x"00",x"04",x"09",x"00",x"00",
x"00",x"00",x"00",x"00",x"00",x"00",x"00",x"00"

);
BEGIN

	index <= to_integer(unsigned(addr));
	dout <= memory(index);

END dataflow;
