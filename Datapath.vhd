
-------------------------------------------------------------------------------
--! @file       Datapath.vhd
--! @author     William Diehl
--! @brief      
--! @date       4 Dec 2016
-------------------------------------------------------------------------------

-- SoftCore Datapath

library ieee;
use ieee.std_logic_1164.all; 
use ieee.std_logic_unsigned.all;  
use IEEE.NUMERIC_STD.ALL;

entity Datapath is

	generic (
		G_DMEM_SIZE : integer:= 16;
		G_PMEM_SIZE : integer:= 12
		);

	port (

		clk : in std_logic;

		-- ext data signals

		extdaddr 	: in std_logic_vector(15 downto 0);
		extdout		: out std_logic_vector(7 downto 0);
		extdin		: in std_logic_vector(7 downto 0);
		extprogin	: in std_logic_vector(7 downto 0);
		extPC		: in std_logic_vector(11 downto 0);
		
		startloc	: in std_logic_vector(11 downto 0);
		endloc		: in std_logic_vector(11 downto 0);

		-- ext control signals

		extprogwrite	: in std_logic;
		extmemwrite	: in std_logic;
		extwrite        : in std_logic;
		done		: out std_logic;

		-- int control signals

		PCen		: in std_logic;
		SPen		: in std_logic;
		SRen		: in std_logic;

		regwrite	: in std_logic;
		memwrite	: in std_logic;
		dstsel		: in std_logic;
		dregsel		: in std_logic_vector(2 downto 0);
		dextregsel	: in std_logic_vector(2 downto 0);
		rxsel		: in std_logic_vector(2 downto 0);
		PCsel		: in std_logic_vector(1 downto 0);
		dinsel		: in std_logic_vector(2 downto 0);
		SPsel		: in std_logic_vector(1 downto 0);
		SRsel		: in std_logic;
		SRsrcsel	: in std_logic_vector(1 downto 0);
		SPaddsel	: in std_logic;
		PCabssel	: in std_logic_vector(1 downto 0);
		PChighregsel	: in std_logic_vector(1 downto 0);
		progword	: out std_logic_vector(7 downto 0);
		SR_out	        : out std_logic_vector(7 downto 0)
		);

end Datapath;

architecture structural of Datapath is
 
constant SPinit : std_logic_vector(15 downto 0):= (OTHERS => '1'); --  initial stack pointer

signal PChighregen: std_logic;

signal dstreg : std_logic_vector(1 downto 0);
signal rxnext : std_logic_vector(7 downto 0);
signal r0, r1, r2, r3 : std_logic_vector(7 downto 0);
signal PC, PCnext, PCabs, PCbxx : std_logic_vector(11 downto 0);
signal paddr : std_logic_vector(15 downto 0);
signal SP : std_logic_vector(15 downto 0);

signal r0en, r1en, r2en, r3en : std_logic;
signal r0dec, r1dec, r2dec, r3dec : std_logic;
signal ALUop1sel, ALUop2sel : std_logic_vector(1 downto 0);
signal ALU2opsel : std_logic_vector(3 downto 0);
signal ALUop1, ALUop2, ALU1out, ALU2out: std_logic_vector(7 downto 0);
signal ALU2add, ALU2sub, ALU2and, ALU2lor, ALU2xor, ALU2ror, ALU2rol : std_logic_vector(7 downto 0);
signal ALU2gf2, ALU2gf3, ALU2gf4 : std_logic_vector(7 downto 0);
signal ALU2gf4_lsn : std_logic_vector(3 downto 0);
signal ALU2add9, ALU1inc9 : std_logic_vector(8 downto 0);
signal ALU1inc, ALU1dec, ALU1not : std_logic_vector(7 downto 0);
signal ALU2addc, ALU1incc : std_logic;
signal SR_ALUin, SRnext : std_logic_vector(7 downto 0);
signal C_ALUin, Z_ALUin, N_ALUin, Cnext, Znext, Nnext : std_logic;
signal dstdecin : std_logic_vector(1 downto 0);
signal prog_out, next_prog_out, dout : std_logic_vector(7 downto 0);
signal TRF0out, TRF1out, TRF2out, TRF3out, TRFout : std_logic_vector(7 downto 0);
signal TRFsel : std_logic_vector(1 downto 0);
signal SPin, SPpX : std_logic_vector(15 downto 0);
signal din, ddin : std_logic_vector(7 downto 0);
signal we : std_logic;
signal daddr, ddaddr : std_logic_vector(15 downto 0);
signal ddaddrl, ddaddru : std_logic_vector(7 downto 0);
signal PChighregin, PChighreg : std_logic_vector(3 downto 0);
signal PCabsl : std_logic_vector(7 downto 0);
signal SR : std_logic_vector(7 downto 0);
 
begin

-- general use registers

with rxsel select
    	rxnext <= ALUop1 when "000",			
		  dout   when "001",			
	          prog_out when "010",			
	          ALU1out when "011",
		  ALU2out when "100",
		  TRFout when "101",
		  ALU2xor when "110",
	          ALUop1 when others;

r0en <= regwrite and r0dec;

store_r0: entity work.regn(behavioral)
	generic map(n=>8)
	port map(
		d => rxnext,
		clk => clk,
		en => r0en,
		q => r0);

r1en <= regwrite and r1dec;

store_r1: entity work.regn(behavioral)
	generic map(n=>8)
	port map(
		d => rxnext,
		clk => clk,
		en => r1en,
		q => r1);

r2en <= regwrite and r2dec;

store_r2: entity work.regn(behavioral)
	generic map(n=>8)
	port map(
		d => rxnext,
		clk => clk,
		en => r2en,
		q => r2);

r3en <= regwrite and r3dec;

store_r3: entity work.regn(behavioral)
	generic map(n=>8)
	port map(
		d => rxnext,
		clk => clk,
		en => r3en,
		q => r3);

-- end registers

-- ALU common selectors

-- src

ALUop1sel <= prog_out(3 downto 2);

with ALUop1sel select
	ALUop1 <= r0 when "00",
		   r1 when "01",
		   r2 when "10",
		   r3 when "11",
		   r3 when others;

-- dst

ALUop2sel <= prog_out(1 downto 0);

with ALUop2sel select
	ALUop2 <= r0 when "00",
		  r1 when "01",
		  r2 when "10",
		  r3 when "11",
		  r3 when others;

-- ALU 1

ALU1inc9 <= ('0' & ALUop2) + 1;
ALU1inc <= ALU1inc9(7 downto 0);
ALU1incc <= ALU1inc9(8);

ALU1dec <= ALUop2 - 1;
ALU1not <= not ALUop2;

with ALUop1sel select
	ALU1out <= ALU1inc when "00",
		   ALU1dec when "01",
		   ALU1not when "10",
		   ALUop2 when others;

-- ALU2

ALU2add9 <= ('0' & ALUop1) + ('0' & ALUop2);
ALU2add <= ALU2add9(7 downto 0);
ALU2addc <= ALU2add9(8);

ALU2sub <= ALUop1 - ALUop2;
ALU2and <= ALUop1 and ALUop2;
ALU2lor <= ALUop1 or ALUop2;
ALU2xor <= ALUop1 xor ALUop2;

ALU2opsel <= prog_out(7 downto 4);

-- 0000 = ADD
-- 0001 = SUB
-- 0010 = AND
-- 0011 = (L)OR
-- 0100 = ROR
-- 0101 = SLR
-- 0110 = ROL
-- 0111 = SLL
--------------- optional additional functions
-- 1000 = GF4 (GF(2^4) mod x^4 + x + 1)
-- 1001 = GF2 (GF(2^8) mod x^8 + x^4 + x^3 + x + 1)
-- 1010 = GF3 (GF(2^8) mod x^8 + x^4 + x^3 + x + 1)

rot_right: entity work.rotate_right(structural)
	port map(
		input => ALUop2,
   	        distance => ALUop1(2 downto 0),
		shift => ALU2opsel(0),
		result => ALU2ror
		);

rot_left: entity work.rotate_left(structural)
	port map(
		input => ALUop2,
		distance => ALUop1(2 downto 0),
		shift => ALU2opsel(0),
		result => ALU2rol
		);

-- optional ALU2 instructions for AES GF2 and GF3 multiplication
gfmul : entity work.GF_mul(dataflow)
	port map(
		input => ALUop1,
		gf2out => ALU2gf2,
		gf3out => ALU2gf3
		);
		
-- optional ALU2 instructions for LED GF4 (GF2^4) multiplication
--gf4mul : entity work.GF4multiply(structural)
--	port map(
--		a => ALUop1(3 downto 0),
--		b => ALUop2(3 downto 0),
--		y => ALU2gf4_lsn
--		);

--ALU2gf4 <= x"0" & ALU2gf4_lsn;
-- end optional ALU2 instructions for LED GF4 multiplication

with ALU2opsel select
	ALU2out <= ALU2add when "0000",
		   ALU2sub when "0001",
		   ALU2and when "0010",
		   ALU2lor when "0011",
		   ALU2ror when "0100",
     		   ALU2ror when "0101",
		   ALU2rol when "0110",
		   ALU2rol when "0111",
--	           ALU2gf4 when "1000", -- optional for GF4 multiplication
		   ALU2gf2 when "1001",
		   ALU2gf3 when "1010",
		   ALUop2 when others;

-- end ALU

-- status register
-- -|-|-|-|-|C|N|Z
-- C = set on carry
-- Z = set on zero
-- N = set on negative

SR_ALUin <= ALU1out when (SRsel ='1') else ALU2out;

C_ALUin  <= ALU1incc when (SRsel = '1') else ALU2addc;
N_ALUin <= '1' when (SR_ALUin(7) = '1') else '0';
Z_ALUin <= '1' when (SR_ALUin = 0) else '0';

with SRsrcsel select
	     Cnext <= '0' when "00",
		      C_ALUin when "01",
		      dout(2) when "10",
		      '0' when others;

with SRsrcsel select
	Nnext <= '0' when "00",
		  N_ALUin when "01",
		  dout(1) when "10",
		  '0' when others;

with SRsrcsel select
	Znext <= '0' when "00",
		  Z_ALUin when "01",
		  dout(0) when "10",
		  '0' when others;

SRnext <= "00000" & Cnext & Nnext & Znext;

store_SR: entity work.regn(behavioral)
	generic map(n=>8)
	port map(
		d => SRnext,
		clk => clk,
		en => SRen,
		q => SR);
  
SR_out <= SR;

-- end status register

-- destination decoder

dstdecin <= prog_out(1 downto 0) when (dstsel = '0') else dstreg;

store_dstreg: entity work.regn(behavioral)
	generic map(n=>2)
	port map(
		d => prog_out(1 downto 0),
		clk => clk,
		en => '1',
		q => dstreg);

r0dec <= '1' when (dstdecin = "00") else '0';
r1dec <= '1' when (dstdecin = "01") else '0';
r2dec <= '1' when (dstdecin = "10") else '0';
r3dec <= '1' when (dstdecin = "11") else '0';

-- end destination decoder

-- Transformation Function 

TRF0: entity work.TRF_AES_0(dataflow) --TRF0(dataflow)
	generic map (TRF_SIZE => 8)
	port map(
		din => ALUop2,
		dout => TRF0out
		);

--TRF1: entity work.TRF_AES_1(dataflow)
--	generic map (TRF_SIZE => 8)
--	port map(
--		din => ALUop2,
--		dout => TRF1out
--		);

--TRF2: entity work.TRF_AES(dataflow) --TRF2(dataflow)
--	generic map (TRF_SIZE => 8)
--	port map(
--		din => ALUop2,
--		dout => TRF2out
--		);

--TRF3: entity work.TRF_AES(dataflow) --TRF3(dataflow)
--	generic map (TRF_SIZE => 8)
--	port map(
--		din => ALUop2,
--		dout => TRF3out
--		);

TRFsel <= prog_out(3 downto 2); 

with TRFsel select
	TRFout <= TRF0out when "00",
		  --TRF1out when "01",
		  --TRF2out when "10",
		  --TRF3out when "11",
		  TRF0out when others;

-- stack pointer

with SPsel select
	SPin <= SPinit when "00",
		SPinit when "01",
		(SP + 1) when "10",
	        (SP - 1) when "11",
		SPinit when others;

store_SP: entity work.regn(behavioral)
	generic map(n=>16)
	port map(
		d => SPin,
		clk => clk,
		en => SPen,
		q => SP);

SPpX <= (SP + 1) when (SPaddsel = '1') else (SP + 2);

-- data memory

with dinsel select
	ddin <= r0 when "000",
                r1 when "001",
                r2 when "010",
	        r3 when "011",
                SR when "100",
	        (PC(7 downto 0) + 1) when "101",
		(x"0" & PC(11 downto 8)) when "111",
		x"00" when others;

din <= ddin when (extwrite = '0') else extdin; -- external memory write
we <= memwrite when (extwrite = '0') else extmemwrite;
daddr <= ddaddr when (extwrite = '0') else extdaddr;

with dregsel select
	ddaddrl <= r0 when "000",
                 r1 when "001",
                 r2 when "010",
                 r3 when "011",
		 SP(7 downto 0) when "100",
		 SPpX(7 downto 0) when "110",
		 x"00" when others;

with dextregsel select
	ddaddru <= r1 when "000",
                   r3 when "001",
                   x"00" when "010",
                   x"00" when "011",
		   SP(15 downto 8) when "100",
		   SPpX(15 downto 8) when "110",
		   x"00" when others;

ddaddr <= ddaddru & ddaddrl;
 
--! Note: Addressable data RAM is 2^G_DMEM_SIZE bytes
--! Default of G_DMEM_SIZE is 16 = 2^16 = 64K RAM

dataMemory: entity work.DRAM(behavioral)
	generic map( MEM_SIZE => G_DMEM_SIZE)
	port map(
			clk => clk,
			we => we,
	                di => din,
			do => dout,
			addr => daddr);

extdout <= dout;

-- program counter and control logic

with PChighregsel select
	PChighregin <= prog_out(3 downto 0) when "00",
		       prog_out(3 downto 0) when "01",
		       dout(3 downto 0) when "10", -- RET
		       PC(11 downto 10) & prog_out(1 downto 0) when "11", -- BXI
		       prog_out(3 downto 0) when others;

store_PChighreg: entity work.regn(behavioral)
	generic map(n=>4)
	port map(
		d => PChighregin,
		clk => clk,
		en => '1',
		q => PChighreg);

with PCabssel select
	PCabsl <= ALUop2 when "00", -- r3, r2, r1, r0 in dst field - BXX
		  ALUop2 when "01", -- r3, r2, r1, r0 in dst field - BXX
 		  dout when "10", -- RET
		  prog_out when "11", -- BXI, JSR, JMP
		  prog_out when others;

PCabs <= PChighreg & PCabsl;
PCbxx <= PC(11 downto 8) & PCabsl;

with PCsel select
	PCnext <= startloc when "00",
                  PCbxx when "01",
		 (PC + 1) when "10",
                 PCabs when "11",
		 (PC + 1) when others;

store_PC: entity work.regn(behavioral)
	generic map(n=>12)
	port map(
		d => PCnext,
		clk => clk,
		en => PCen,
		q => PC);

done <= '1' when (PC = endloc) else '0';

-- paddr uses PCnext due to pipelining of program word from memory
paddr <= (x"0" & PCnext) when (extprogwrite = '0') else (x"0" & extPC);

--! Max Program memory is 2^12  

progMemory: entity work.DRAM(behavioral)
	generic map( MEM_SIZE => G_PMEM_SIZE)
	port map(
		clk => clk,
		we => extprogwrite, -- program memory cannot be written inside softcore
	        di => extprogin, 
		do => next_prog_out,  
		addr => paddr);

--! The prog_out register is pipelined to reduce critical path

store_prog_out: entity work.regn(behavioral)
	generic map(n=>8)
	port map(
		d => next_prog_out,
		clk => clk,
		en => PCen,
		q => prog_out);

progword <= prog_out;

end structural; 
