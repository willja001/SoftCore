-- loader_ctrl
-- William Diehl
-- George Mason University

-- Sep 2016

LIBRARY ieee;
USE ieee.std_logic_1164.all;
USE ieee.std_logic_unsigned.all;

ENTITY loader_ctrl IS

PORT(

	clk : in std_logic;
	rst : in std_logic;

	progload : out std_logic;
	progloadend	  : in std_logic;

	dataload : out std_logic;
	dataloadend   : in std_logic;

	dataread : out std_logic;
	datareadend   : in std_logic;
	
	runstart : out std_logic;
	runend	:  in std_logic
	
	);
	
END loader_ctrl;

ARCHITECTURE behavioral OF loader_ctrl IS

SIGNAL Pstate, Nstate : STD_LOGIC_VECTOR(3 DOWNTO 0);
 
BEGIN

sync_process: PROCESS(clk, rst)
BEGIN

-- Requires 1 asynchronous reset to put in State 0

IF (rst = '1') THEN
	Pstate <= x"0";
	
-- All state transitions occur on rising edge
-- All transitions are disabled if Read/Write Enable is low

ELSIF (rising_edge(clk)) 
	 THEN Pstate <= Nstate;
	     
END IF;
	
END Process;

public_process: PROCESS(Pstate, progloadend, dataloadend, datareadend, runend)
BEGIN
 
	 -- defaults
progload <= '0';
dataload <= '0';
runstart <= '0'; 
dataread <= '0';

case Pstate is

	 WHEN x"0" =>
	 
	 Nstate <= x"1";

	 WHEN x"1" =>
	 
	 progload <= '1';
	 Nstate <= x"2";
	 
	 WHEN x"2" => 
	 
	 if (progloadend = '1') then
		Nstate <= x"3";
	 else 
	   Nstate <= x"2";
	 end if;
	 
	 progload <= '1';
		
	WHEN x"3" => 
		
		dataload <= '1';
		Nstate <= x"4";
	
	WHEN x"4" => 
	
		if (dataloadend = '1') then
		runstart <= '1';
		Nstate <= x"5";
	 else 
	   Nstate <= x"4";
	 end if;
	 
	 dataload <= '1';
	
	WHEN x"5" => 
	
	   
		Nstate <= x"6";
		
	WHEN x"6" =>

	if (runend = '1') then
		Nstate <= x"7";
	 else 
	   Nstate <= x"6";
	 end if;

	WHEN x"7" => 

		dataread <= '1';
		Nstate <= x"8";

	WHEN x"8" => 
	
		if (datareadend = '1') then
		Nstate <= x"9";
	 else 
	   Nstate <= x"8";
	 end if;

		dataread <= '1';

	WHEN x"9" => 
	
		Nstate <= x"9";
		
	WHEN others => 

		Nstate <= x"9";
			
end case;

END Process;
		
END behavioral;  