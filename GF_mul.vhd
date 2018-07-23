-- GF_mul

----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

--use IEEE.NUMERIC_STD.ALL;

entity GF_mul is
    Port ( input : in  STD_LOGIC_VECTOR (7 downto 0);
           gf2out : out  STD_LOGIC_VECTOR (7 downto 0);
	   gf3out : out std_logic_vector(7 downto 0)
	 );
end GF_mul;

architecture dataflow of GF_mul is

signal a : std_logic_vector(7 downto 0);
signal gf2 : std_logic_vector(7 downto 0);

begin

  -- GCM polynomial a^8 + a^4 + a^3 + a + 1
  
a <= input(6 downto 0) & '0';
gf2 <= a when (input(7)='0') else (a xor "00011011");
gf2out <= gf2;
gf3out <= gf2 xor input;

end dataflow;

