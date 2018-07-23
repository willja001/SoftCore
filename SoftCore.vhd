
-------------------------------------------------------------------------------
--! @file       SoftCore.vhd
--! @author     William Diehl
--! @brief      
--! @date       11 Sep 2016
-------------------------------------------------------------------------------

-- SoftCore

library ieee;
use ieee.std_logic_1164.all; 
use ieee.std_logic_unsigned.all;  
use IEEE.NUMERIC_STD.ALL;

entity SoftCore is

generic (
        --! Data memory size
        G_DMEM_SIZE	: integer := 6; -- Default to 2^8 bytes of data RAM
												 -- Max is 2^16 bytes of data RAM
	--! Program memory size
        G_PMEM_SIZE	: integer := 9 -- Default to 2^8 bytes of program RAM
												-- Max is 2^12 bytes of data RAM
    );

port(

	clk : in std_logic;
	rst : in std_logic;
	--en  : in std_logic;

-- data signals

	extdaddr	 	: in std_logic_vector(15 downto 0);
	extdout		: out std_logic_vector(7 downto 0);
	extdin		: in std_logic_vector(7 downto 0);
	extprogin	: in std_logic_vector(7 downto 0);
	extPC		: in std_logic_vector(11 downto 0);
		
	startloc	: in std_logic_vector(11 downto 0);
	endloc		: in std_logic_vector(11 downto 0);

-- control signals

	extprogwrite		: in std_logic;
	extmemwrite		: in std_logic;
	extwrite		 : in std_logic;
	start			: in std_logic;
	done_out		: out std_logic

);

end SoftCore;

architecture structural of SoftCore is
 
signal PCen: std_logic;
signal SPen: std_logic;
signal SRen: std_logic;

signal regwrite, memwrite : std_logic;
signal dstsel : std_logic;
signal dregsel : std_logic_vector(2 downto 0);
signal dextregsel : std_logic_vector(2 downto 0);
signal rxsel : std_logic_vector(2 downto 0);
signal PCsel: std_logic_vector(1 downto 0);
signal dinsel : std_logic_vector(2 downto 0);
signal SPsel  : std_logic_vector(1 downto 0);
signal SRsel  : std_logic;
signal SRsrcsel : std_logic_vector(1 downto 0);
signal SPaddsel : std_logic;
signal PCabssel : std_logic_vector(1 downto 0);
signal PChighregsel: std_logic_vector(1 downto 0);
signal progword : std_logic_vector(7 downto 0);
signal SR : std_logic_vector(7 downto 0);

signal done : std_logic;
 
begin

done_out <= done;

softCoreDataPath: entity work.Datapath(structural)
	generic map(
		G_DMEM_SIZE => G_DMEM_SIZE,
		G_PMEM_SIZE => G_PMEM_SIZE
		)

	port map(

		clk => clk,

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
		extmemwrite => extmemwrite,
		extwrite => extwrite,
		done => done,

		-- int control signals

		PCen => PCen,
		SPen => SPen,
		SRen => SRen,

		regwrite => regwrite,
		memwrite => memwrite,
		dstsel => dstsel,
		dregsel => dregsel,
		dextregsel => dextregsel,
		rxsel => rxsel,
		PCsel => PCsel,
		dinsel => dinsel,
		SPsel => SPsel,
		SRsrcsel => SRsrcsel,
		SRsel => SRsel,
		SPaddsel => SPaddsel,
		PCabssel => PCabssel,
		PChighregsel => PChighregsel,
		progword => progword,
		SR_out => SR
		);

softCoreCtrl: entity work.Controller(behavioral)

	port map(

		clk => clk,
		rst => rst,

		-- ext control signals

		start => start,
		done => done,
		--done_out => done_out,

		-- int control signals

		PCen => PCen,
		SPen => SPen,
		SRen => SRen,

		regwrite => regwrite,
		memwrite => memwrite,
		dstsel => dstsel,
		dregsel => dregsel,
		dextregsel => dextregsel,
		rxsel => rxsel,
		PCsel => PCsel,
		dinsel => dinsel,
		SPsel => SPsel,
		SRsrcsel => SRsrcsel,
		SRsel => SRsel,
		SPaddsel => SPaddsel,
		PCabssel => PCabssel,
		PChighregsel => PChighregsel,
		progword => progword,
		SR => SR
		);

end structural; 