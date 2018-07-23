----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;


entity loader_tb is

end loader_tb;

architecture behavioral of loader_tb is

signal clk: std_logic:='0';
signal rst: std_logic;

begin


uut: entity work.loader(structural)
	generic map(G_PMEM_SIZE => 9, G_DMEM_SIZE => 6)

	port map(
	clk => clk,
	rst => rst
	);

clk <= not clk after 4 ns;

init_process: process
begin
		rst <= '1';
		wait for 4 ns;
		rst <= '0';
		wait;
end process;

end behavioral;

