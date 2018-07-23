-- Controller
-- William Diehl
-- George Mason University

-- v1.1 Verified for correct operation on Spartan-6 xc6slx16csg324-3
-- 4 June 2018

LIBRARY ieee;
USE ieee.std_logic_1164.all;
USE ieee.std_logic_unsigned.all;

ENTITY Controller IS

PORT(

        clk: in std_logic;
	rst: in std_logic;
        start : in std_logic;
	done : in std_logic;
	progword : in std_logic_vector(7 downto 0);
	SR : in std_logic_vector(7 downto 0);
	
	PCsel : out std_logic_vector(1 downto 0);
	PChighregsel : out std_logic_vector(1 downto 0);
	PCabssel : out std_logic_vector(1 downto 0);
	SPsel : out std_logic_vector(1 downto 0);
	SPaddsel : out std_logic;
	SRsrcsel : out std_logic_vector(1 downto 0);
	SRsel : out std_logic;
	regwrite : out std_logic;
	memwrite : out std_logic;
	dstsel : out std_logic;
	rxsel : out std_logic_vector(2 downto 0);
	dregsel : out std_logic_vector(2 downto 0);
	dextregsel : out std_logic_vector(2 downto 0);
	dinsel : out std_logic_vector(2 downto 0);
	
	PCen : out std_logic;
	SRen : out std_logic;
	SPen : out std_logic
	
	);
	
END Controller;

ARCHITECTURE behavioral OF Controller IS

SIGNAL PS, NS : STD_LOGIC_VECTOR(3 DOWNTO 0);
signal opcode : std_logic_vector(3 downto 0);
signal op, src, dst : std_logic_vector(1 downto 0);
signal opreg : std_logic_vector(1 downto 0):="00";
signal Z, N, C : std_logic;
signal donereg : std_logic:='0';
 
BEGIN

opcode <= progword(7 downto 4);
op <= progword(3 downto 2);
src <= progword(3 downto 2);
dst <= progword(1 downto 0);
Z <= SR(0);
N <= SR(1);
C <= SR(2);

sync_process: PROCESS(clk, start)
BEGIN


IF (rising_edge(clk)) THEN
	if (rst = '1') then
	   PS <= x"8"; -- idle state
	else
	   donereg <= done;
	   opreg <= op;
	   PS <= NS;
	END if;
	  
END IF;
	
END Process;

public_process: PROCESS(PS, src, dst, opcode, op, opreg, Z, N, C, start, donereg)
BEGIN
 
	 -- defaults
PCen <= '0';
PCsel <= "00";
regwrite <= '0';
memwrite <= '0';
dstsel <= '0';
SPen <= '0';
SPaddsel <= '0';
SRen <= '0';
SRsel <= '0';
PChighregsel <= "00";
SPsel <= "00";
SRsrcsel <= "00";
rxsel <= "000";
dregsel <= "000";
dextregsel <= "000";
dinsel <= "000";
PCabssel <= "00";

NS <= x"8";

outercase: case PS is
		 		 
	 WHEN x"0" => -- s_init
-- Initialization after start	
			SPen <= '1';
			PCsel <= "00"; -- reset PC
			PCen <= '1';
			SRen <= '1'; -- reset SR
			NS <= x"1";
				 
	 WHEN x"1" => -- State 1
	 	
	 if (donereg = '1') then
	 	PCsel <= "00"; -- reset PC
		PCen <= '1';
		NS <= x"8";	-- idle state
	 else 

		case opcode is
	 	
		when "0000" => -- LDS [src], dst

			regwrite <= '1';
			dstsel <= '0';
			rxsel <= "001";
			dregsel <= "0" & src;
			dextregsel <= "010";
			PCsel <= "10";
			PCen <= '1';
			NS <= x"1";

		when "0001" => -- LDL [src16], dst
			
			regwrite <= '1';
			dstsel <= '0';
			rxsel <= "001";
			dregsel <= "0" & src;
			dextregsel <= "00" & src(0);
			PCsel <= "10";
			PCen <= '1';
			NS <= x"1";

		when "0010" => -- STS src, [dst]

			memwrite <= '1';
			dinsel <= "0" & src;
			dregsel <= "0" & dst;
			dextregsel <= "010";
			PCsel <= "10";
			PCen <= '1';
			NS <= x"1";

		when "0011" => -- STL src, [dst16]

			memwrite <= '1';
			dinsel <= "0" & src;
			dregsel <= "0" & dst;
		        dextregsel <= "00" & dst(0);
			PCsel <= "10";
			PCen <= '1';
			NS <= x"1";

		when "0100" => -- MOV src, dst

			regwrite <= '1';
			rxsel <= "000";
			dstsel <= '0';
			PCsel <= "10";
			PCen <= '1';
			NS <= x"1";

		when "0101" => -- MVI dst (1st cycle)

			PCsel <= "10";
			PCen <= '1';
			NS <= x"2";

		when "0110" => -- ALU op, dst (1 cycle) or ALU src, dst (2 cycle) 

			if (op = "11") then
				NS <= x"3";
			else 
				dstsel <= '0';
				rxsel <= "011";
				regwrite <= '1';
				SRsel <= '1';
				SRsrcsel <= "01";
				SRen <= '1';
				NS <= x"1";
			end if;
		
			PCsel <= "10";
			PCen <= '1';

		when "0111" => -- STR SR, [SP]

			memwrite <= '1';
			dinsel <= "100";
			dregsel <= "100"; 
			dextregsel <= "100";
			SPsel <= "11"; -- SP = SP - 1
			SPen <= '1';
			PCsel <= "10";
			PCen <= '1';
			NS <= x"1";
		
		when "1000" => -- LSR [SP+1], SR

			SPaddsel <= '1';
			dregsel <= "110";
			dextregsel <= "110";
			SPsel <= "10";
			SPen <= '1';
			SRsrcsel <= "10";
			SRen <= '1';
			PCsel <= "10";
			PCen <= '1';
			NS <= x"1";

		when "1001" => -- JSR 4 + 8 (1 cycle)

			dinsel <= "111";
			memwrite <= '1';
			dregsel <= "100";
			dextregsel <= "100";
			SPsel <= "11";
			SPen <= '1';
			PChighregsel <= "00";
			PCsel <= "10";
			PCen <= '1';
			NS <= x"4";
			
		when "1010" => -- RET

			PChighregsel <= "10";
			dregsel <= "110";
			dextregsel <= "110";
			SPaddsel <= '0';
			SPsel <= "10";
			SPen <= '1';
			NS <= x"5";
			
		when "1011" => -- XOR src, dst
		
			regwrite <= '1';
			rxsel <= "110";
			dstsel <= '0';
			PCsel <= "10";
			PCen <= '1';
			NS <= x"1";	
			
		when "1100" => -- TRF op, dst

			regwrite <= '1';
			rxsel <= "101";
			dstsel <= '0';
			PCsel <= "10";
			PCen <= '1';
			NS <= x"1";	
			
		when "1101" => -- JMP htarget(4), ltarget(8) (1st cycle)
				
			PChighregsel <= "00";
			PCsel <= "10";
			PCen <= '1';
			NS <= x"6";
			
		when "1110" => -- BXX op, [dst]
		
			case op is

				when "00" => -- conditional branch on C
				
				if (C = '1') then
					PCsel <= "01";
				else
					PCsel <= "10";
				end if;
				
				when "01" => -- conditional branch on N
				
				if (N = '1') then
					PCsel <= "01";
				else
					PCsel <= "10";
				end if;
				
				when "10" => -- conditional branch on Z
				
				if (Z = '1') then
					PCsel <= "01";
				else
					PCsel <= "10";
				end if;
				
				when others => 
				
				PCsel <= "10";
				
			end case;
		
			PCabssel <= "00";
			PCen <= '1';
			SRsrcsel <= "00";
			SRen <= '1'; -- reset SR
			NS <= x"1";
			
		when "1111" => -- BXI op, htarget, ltarget (1st cycle)
			
			--opreg <= op; -- save and interpret on the next clock cycle
			PChighregsel <= "11";
			PCsel <= "10";
			PCen <= '1';
			NS <= x"7";
			
		when others =>
		
			NS <= x"1";
			
		end case;
	end if;
	
	WHEN x"2" => -- MVI dst (2nd cycle)

		regwrite <= '1';
		rxsel <= "010"; -- choose Im
		dstsel <= '1'; -- choose dstreg
		PCsel <= "10";
		PCen <= '1';
		NS <= x"1";

	WHEN x"3" => -- ALU src, dst (2nd cycle)	

		regwrite <= '1';
		rxsel <= "100";
		dstsel <= '0';
		SRsrcsel <= "01";
		SRen <= '1';
		PCsel <= "10";
		PCen <= '1';
		NS <= x"1";					
	
	WHEN x"4" => -- JSR (2nd cycle)

		dinsel <= "101";
		memwrite <= '1';
		dregsel <= "100";
		dextregsel <= "100";
		SPsel <= "11";
		SPen <= '1';
		PCabssel <= "11";
		PCsel <= "11";
		PCen <= '1';
		NS <= x"1";

	WHEN x"5" => -- RET (2nd cycle)

		dregsel <= "100";
		dextregsel <= "100";
		SPsel <= "10";
		SPen <= '1';
		PCabssel <= "10";
     	        PCsel <= "11";
		PCen <= '1';
		NS <= x"1";

	WHEN x"6" => -- JMP htarget(4), ltarget(8) (2nd cycle)
	
		PCabssel <= "11";
		PCsel <= "11";
		PCen <= '1';
		NS <= x"1";
		
	WHEN x"7" => -- JMP htarget(4), ltarget(8) (2nd cycle)
	
		case opreg is

				when "00" => -- conditional branch on C
				
				if (C = '1') then
					PCsel <= "11";
				else
					PCsel <= "10";
				end if;
				
				when "01" => -- conditional branch on N
				
				if (N = '1') then
					PCsel <= "11";
				else
					PCsel <= "10";
				end if;
				
				when "10" => -- conditional branch on Z
				
				if (Z = '1') then
					PCsel <= "11";
				else
					PCsel <= "10";
				end if;
								
				when others => 
				
				PCsel <= "10";
				
			end case;
			
		PCabssel <= "11";
		PCen <= '1';
		SRen <= '1'; -- reset SR
		NS <= x"1";
		
	WHEN x"8" => -- idle state
	
		if (start = '1') then
			NS <= x"0";
		else
			
			NS <= x"8";
		end if;
		
	WHEN OTHERS =>
	
		  NS <= x"1";
			  
	end case outercase; 

END Process;
		
END behavioral;  
