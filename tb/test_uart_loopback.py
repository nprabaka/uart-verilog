import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly, ClockCycles

CLKS_PER_BIT = 868


async def reset(dut):
    dut.rst.value = 1
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0
    await ClockCycles(dut.clk, 2)


async def wait_for_byte(dut):
    """Same as in the RX test: wait for rx_valid, return the byte."""
    for _ in range(CLKS_PER_BIT * 12):
        await RisingEdge(dut.clk)
        await ReadOnly()
        if dut.rx_valid.value == 1:
            return int(dut.rx_data.value)
    assert False, "rx_valid never pulsed: no byte received"


@cocotb.test()
async def test_loopback(dut):
    """Bytes sent by TX must come back out of RX unchanged."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)

    for value in [0x41, 0x00, 0xFF, 0x55, 0xAA]:
        waiter = cocotb.start_soon(wait_for_byte(dut))

        dut.tx_data.value = value          # same as send_byte in the TX test
        dut.tx_start.value = 1
        await RisingEdge(dut.clk)
        dut.tx_start.value = 0

        got = await waiter
        await RisingEdge(dut.clk)
        assert got == value, f"sent {value:#04x}, received {got:#04x}"
        assert dut.frame_error.value == 0, "unexpected frame error"

        while dut.tx_busy.value == 1:       # wait for TX to finish
            await RisingEdge(dut.clk)