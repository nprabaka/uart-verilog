import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles

CLKS_PER_BIT = 868


async def reset(dut):
    """Hold reset for a few cycles, with inputs at safe values."""
    dut.rst.value = 1
    dut.tx_start.value = 0
    dut.data.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0
    await ClockCycles(dut.clk, 2)


async def send_byte(dut, byte):
    """Act like the outside world: put a byte on 'data' and pulse tx_start."""
    dut.data.value = byte
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    dut.tx_start.value = 0


async def read_tx_byte(dut):
    """Act like a receiver: watch the tx wire and decode one byte."""
    await FallingEdge(dut.tx)                        # start bit begins (1 -> 0)
    await ClockCycles(dut.clk, CLKS_PER_BIT // 2)    # move to the middle of it
    assert dut.tx.value == 0, "start bit should be 0"

    byte = 0
    for i in range(8):
        await ClockCycles(dut.clk, CLKS_PER_BIT)     # middle of the next bit
        byte |= int(dut.tx.value) << i               # LSB first

    await ClockCycles(dut.clk, CLKS_PER_BIT)         # middle of the stop bit
    assert dut.tx.value == 1, "stop bit should be 1"
    return byte


@cocotb.test()
async def test_send_letter_A(dut):
    """Send 'A' (0x41) and check it comes out correctly."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)

    assert dut.tx.value == 1, "tx should idle at 1"

    listener = cocotb.start_soon(read_tx_byte(dut))  # start listening first
    await send_byte(dut, 0x41)
    got = await listener

    assert got == 0x41, f"sent 0x41, received {got:#04x}"


@cocotb.test()
async def test_several_bytes(dut):
    """Send tricky patterns back to back."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)

    for value in [0x00, 0xFF, 0x55, 0xAA, 0x41]:
        listener = cocotb.start_soon(read_tx_byte(dut))
        await send_byte(dut, value)
        got = await listener
        assert got == value, f"sent {value:#04x}, received {got:#04x}"

        while dut.tx_busy.value == 1:                 # wait until free again
            await RisingEdge(dut.clk)