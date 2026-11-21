# Usage:  make TOP=baud_gen   or   make TOP=counter
SIM ?= icarus
TOPLEVEL_LANG ?= verilog
TOP ?= baud_gen

VERILOG_SOURCES = $(wildcard $(PWD)/../rtl/*.v)
COCOTB_TOPLEVEL = $(TOP)
COCOTB_TEST_MODULES = test_$(TOP)
SIM_BUILD = sim_build_$(TOP)

include $(shell cocotb-config --makefiles)/Makefile.sim
