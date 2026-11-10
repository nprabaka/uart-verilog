import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly, ClockCycles

@cocotb.test()
async def test_counter_counts(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0

    await RisingEdge(dut.clk)
    await ReadOnly()
    start = int(dut.count.value)

    for i in range(20):
        await RisingEdge(dut.clk)
        await ReadOnly()
        expected = (start + i + 1) % 16
        assert int(dut.count.value) == expected, \
            f"cycle {i}: got {int(dut.count.value)}, expected {expected}"
