import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly, ClockCycles

CLKS_PER_BIT = 868

@cocotb.test()
async def test_tick_spacing(dut):
    """tick must pulse for exactly 1 cycle, every CLKS_PER_BIT cycles"""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0

    tick_cycles = []
    for cycle in range(CLKS_PER_BIT * 5 + 10):
        await RisingEdge(dut.clk)
        await ReadOnly()
        if int(dut.tick.value) == 1:
            tick_cycles.append(cycle)

    assert len(tick_cycles) >= 5, f"only saw {len(tick_cycles)} ticks"

    gaps = [b - a for a, b in zip(tick_cycles, tick_cycles[1:])]
    dut._log.info(f"tick at cycles {tick_cycles}, gaps {gaps}")
    for g in gaps:
        assert g == CLKS_PER_BIT, f"gap was {g}, expected {CLKS_PER_BIT}"
