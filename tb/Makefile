SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(PWD)/../rtl/counter.v
COCOTB_TOPLEVEL = counter
COCOTB_TEST_MODULES = test_counter

include $(shell cocotb-config --makefiles)/Makefile.sim
