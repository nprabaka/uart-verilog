import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly, ClockCycles

CLKS_PER_BIT = 868


async def reset(dut):
    """Press reset. The rx wire idles at 1, like a real UART line."""
    dut.rst.value = 1
    dut.rx.value = 1
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0
    await ClockCycles(dut.clk, 2)


async def drive_byte(dut, byte, stop_bit=1):
    """Act like a transmitter: wiggle the rx wire to send one byte."""
    dut.rx.value = 0                              # start bit
    await ClockCycles(dut.clk, CLKS_PER_BIT)
    for i in range(8):                            # 8 data bits, LSB first
        dut.rx.value = (byte >> i) & 1
        await ClockCycles(dut.clk, CLKS_PER_BIT)
    dut.rx.value = stop_bit                       # stop bit (normally 1)
    await ClockCycles(dut.clk, CLKS_PER_BIT)
    dut.rx.value = 1                              # back to idle


async def wait_for_byte(dut):
    """Watch rx_valid. When it pulses, return the received byte."""
    for _ in range(CLKS_PER_BIT * 12):
        await RisingEdge(dut.clk)
        await ReadOnly()
        if dut.rx_valid.value == 1:
            return int(dut.data.value)
    assert False, "rx_valid never pulsed: no byte received"


async def count_valid_pulses(dut, cycles):
    """Count how many times rx_valid pulses during a time window."""
    count = 0
    for _ in range(cycles):
        await RisingEdge(dut.clk)
        await ReadOnly()
        if dut.rx_valid.value == 1:
            count += 1
    return count


@cocotb.test()
async def test_receive_bytes(dut):
    """Send several bytes into rx and check each one is received."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)

    for value in [0x41, 0x00, 0xFF, 0x55, 0xAA]:
        waiter = cocotb.start_soon(wait_for_byte(dut))  # start watching first
        await drive_byte(dut, value)
        got = await waiter
        assert got == value, f"sent {value:#04x}, received {got:#04x}"
        assert dut.frame_error.value == 0, "unexpected frame error"


@cocotb.test()
async def test_bad_stop_bit(dut):
    """A stop bit of 0 must raise frame_error and NOT pulse rx_valid."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)

    counter = cocotb.start_soon(count_valid_pulses(dut, CLKS_PER_BIT * 11))
    await drive_byte(dut, 0x41, stop_bit=0)
    pulses = await counter

    assert dut.frame_error.value == 1, "frame_error should be 1"
    assert pulses == 0, "rx_valid should not pulse for a bad byte"


@cocotb.test()
async def test_glitch_ignored(dut):
    """A short dip on rx (shorter than half a bit) must be ignored."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)

    counter = cocotb.start_soon(count_valid_pulses(dut, CLKS_PER_BIT * 12))
    dut.rx.value = 0                             # short glitch...
    await ClockCycles(dut.clk, 100)              # ...only 100 cycles
    dut.rx.value = 1
    pulses = await counter

    assert pulses == 0, "a glitch should not produce a byte"