-- ROR rotate right
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
use IEEE.NUMERIC_STD.ALL;


entity rotate_right is
    Port ( input : in  STD_LOGIC_VECTOR (7 downto 0);
           distance : in  STD_LOGIC_VECTOR (2 downto 0);
	        shift : in std_logic;
           result : out  STD_LOGIC_VECTOR (7 downto 0));
end rotate_right;

architecture structural of rotate_right is

signal rorsel1, rorsel2, rorsel4 : std_logic_vector(1 downto 0);
signal ror1, ror2, ror4 : std_logic_vector(7 downto 0);

begin

rorsel1 <= shift & distance(0);
rorsel2 <= shift & distance(1);
rorsel4 <= shift & distance(2);

with rorsel1 select
	ror1 <= input when "00",
		     input(0) & input(7 downto 1) when "01",
		     input when "10",
		     '0' & input(7 downto 1) when "11", 
			  input when others;

with rorsel2 select
	ror2 <= ror1 when "00",
		     ror1(1 downto 0) & ror1(7 downto 2) when "01",
		     ror1 when "10",
		     "00" & ror1(7 downto 2) when "11",
			  ror1 when others;

with rorsel4 select
	ror4 <= ror2 when "00",
		     ror2(3 downto 0) & ror2(7 downto 4) when "01",
		     ror2 when "10",
		     x"0" & ror2(7 downto 4) when "11",
			  ror2 when others;
			  
result <= ror4;			  

end structural;




