
-------------------------------------------------------------------------------
--! @file       loader.vhd
--! @author     William Diehl
--! @brief      
--! @date       11 Sep 2016
-------------------------------------------------------------------------------

-- SoftCore Loader

library ieee;
use ieee.std_logic_1164.all; 
use ieee.std_logic_unsigned.all;  
use IEEE.NUMERIC_STD.ALL;

entity loader is

generic (
        --! Data memory size
        G_DMEM_SIZE	: integer := 6; -- Default to 2^16 bytes of data RAM
	--! Program memory size
        G_PMEM_SIZE	: integer := 9 -- Default to 2^12 bytes of program RAM
    );

port(

	clk : in std_logic;
	rst  : in std_logic
);

end loader;

architecture structural of loader is

constant startloc : std_logic_vector(11 downto 0):=x"000";
constant endloc : std_logic_vector(11 downto 0):=x"01D";
constant endprogloadloc : std_logic_vector(11 downto 0):=x"18C";
constant enddataloc : std_logic_vector(15 downto 0):=x"003F";

constant PROG_LOAD_SIZE : integer:=9;
constant DATA_LOAD_SIZE : integer:=6;
constant PZEROS : std_logic_vector(11 - PROG_LOAD_SIZE downto 0):=(OTHERS => '0');
constant DZEROS : std_logic_vector(15 - DATA_LOAD_SIZE downto 0):=(OTHERS => '0');

signal progload : std_logic;
signal progloadend	  : std_logic;

signal dataload : std_logic;
signal dataloadend   : std_logic;
signal dataread : std_logic;
signal datareadend : std_logic;

signal runstart : std_logic;
signal runend	: std_logic;

signal extprogwrite : std_logic;
signal extPCshort : std_logic_vector(PROG_LOAD_SIZE - 1 downto 0);
signal extPCshortnext: std_logic_vector(PROG_LOAD_SIZE - 1 downto 0);
signal extPC : std_logic_vector(11 downto 0);
signal extprogin : std_logic_vector(7 downto 0);
signal extdout : std_logic_vector(7 downto 0);

signal extdaddr, extdaddrload, extdaddrread : std_logic_vector(15 downto 0):= (OTHERS => '0');
signal extdaddrloadshort, extdaddrreadshort  : std_logic_vector(DATA_LOAD_SIZE - 1 downto 0);
signal extdaddrloadnext, extdaddrreadnext  :  std_logic_vector(DATA_LOAD_SIZE - 1 downto 0);
signal extdin : std_logic_vector(7 downto 0):= (OTHERS => '0');
signal extwrite : std_logic:='0';
signal extmemwrite : std_logic:='0';
 
begin

-- Program Load section
extPCshortnext <= extPCshort + 1;
extPC <= PZEROS & extPCshort; 
progloadend <= '1' when (extPC = endprogloadloc) else '0';

-- Data Load section
extdaddrloadnext <= extdaddrloadshort + 1;
extdaddrload <= DZEROS & extdaddrloadshort; 
dataloadend <= '1' when (extdaddrload = enddataloc) else '0';
extwrite <= '1' when (dataload = '1') else dataread;
extdaddr <= extdaddrload when (dataload = '1') else extdaddrread;

-- Data Load section
extdaddrreadnext <= extdaddrreadshort + 1;
extdaddrread <= DZEROS & extdaddrreadshort; 
datareadend <= '1' when (extdaddrread = enddataloc) else '0';

progloadcntr: entity work.regn(behavioral)
	generic map(N => PROG_LOAD_SIZE)
	port map(
		d => extPCshortnext,
		clk => clk,
		en => progload,
		q => extPCshort
	);

dataloadcntr: entity work.regn(behavioral)
	generic map(N => DATA_LOAD_SIZE)
	port map(
		d => extdaddrloadnext,
		clk => clk,
		en => dataload,
		q => extdaddrloadshort
	);

datareadcntr: entity work.regn(behavioral)
	generic map(N => DATA_LOAD_SIZE)
	port map(
		d => extdaddrreadnext,
		clk => clk,
		en => dataread,
		q => extdaddrreadshort
	);


extprogwrite <= progload;

sftCore: entity work.SoftCore(structural)
	generic map(
		G_DMEM_SIZE => DATA_LOAD_SIZE,
		G_PMEM_SIZE => PROG_LOAD_SIZE
		)

	port map(

		clk => clk,
		rst => rst,

		-- ext data signals

		extdaddr => extdaddr,
		extdout => extdout,
		extdin  => extdin,
		extprogin => extprogin,
		extPC => extPC,
		
		startloc => startloc,
		endloc => endloc,

		-- ext control signals

		extprogwrite => extprogwrite,
		extmemwrite => dataload,
		extwrite => extwrite,
		start => runstart,
		done_out => runend
		
		);

prog: entity work.progloader(dataflow)
	generic map(LOADER_SIZE => PROG_LOAD_SIZE)
	port map (
		addr => extPCshort,
		dout => extprogin
		);
		
data: entity work.dataloader(dataflow)
	generic map(LOADER_SIZE => DATA_LOAD_SIZE)
	port map (
		addr => extdaddrloadshort,
		dout => extdin
		);

ctrl: entity work.loader_ctrl(behavioral)
	port map (
		clk => clk,
		rst => rst,

		progload => progload,
		progloadend => progloadend,
			
		dataload => dataload,
		dataloadend => dataloadend,
		
		dataread => dataread,
		datareadend => datareadend,
		
		runstart => runstart,
		runend => runend
);

end structural; 