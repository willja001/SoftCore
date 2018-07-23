-- ROL rotate left
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
use IEEE.NUMERIC_STD.ALL;


entity rotate_left is
    Port ( input : in  STD_LOGIC_VECTOR (7 downto 0);
           distance : in  STD_LOGIC_VECTOR (2 downto 0);
	   shift : in std_logic;
           result : out  STD_LOGIC_VECTOR (7 downto 0));
end rotate_left;

architecture structural of rotate_left is

signal rolsel1, rolsel2, rolsel4 : std_logic_vector(1 downto 0);
signal rol1, rol2, rol4 : std_logic_vector(7 downto 0);

begin

rolsel1 <= shift & distance(0);
rolsel2 <= shift & distance(1);
rolsel4 <= shift & distance(2);

with rolsel1 select
	rol1 <= input when "00",
		     input(6 downto 0) & input(7) when "01",
		     input when "10",
		     input(6 downto 0) & '0' when "11",
			  input when others;

with rolsel2 select
	rol2 <= rol1 when "00",
		     rol1(5 downto 0) & rol1(7 downto 6) when "01",
		     rol1 when "10",
		     rol1(5 downto 0) & "00" when "11",
			  rol1 when others;

with rolsel4 select
	rol4 <= rol2 when "00",
		     rol2(3 downto 0) & rol2(7 downto 4) when "01",
		     rol2 when "10",
		     rol2(3 downto 0) & x"0" when "11",
			  rol2 when others;
			  
result <= rol4;			  

end structural;




