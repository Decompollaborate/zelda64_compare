MAKEFLAGS += --no-builtin-rules

# Build options can either be changed by modifying the makefile, or by building with 'make SETTING=value'

GAME                   ?= oot
VERSION                ?= ne0
# if SPLIT_FUNCTIONS is non-zero, the disassembler will try to split functions and rodata
SPLIT_FUNCTIONS        ?= 0
# if PRINT_BOUNDARIES is non-zero, the disassembler will print any detected new boundaries
PRINT_BOUNDARIES       ?= 0

DISASM_VERBOSITY       ?= -q
DISASM_EXTRA_PARAMS    ?=
DISASM_EXTRA_PARAMS    += --no-use-fpccsr
DISASM_EXTRA_PARAMS    += --Mreg-names o32
DISASM_EXTRA_PARAMS    += --custom-suffix _unknown
DISASM_EXTRA_PARAMS    += --no-asm-comments
DISASM_EXTRA_PARAMS    += --no-glabel-count
DISASM_EXTRA_PARAMS    += --name-vars-by-file
DISASM_EXTRA_PARAMS    += --sequential-label-names

ifeq ($(GAME), dnm)
  DISASM_EXTRA_PARAMS  += --reloc-separate
endif

# TODO: implement?
DISASM_FUNC_SPLIT      =
ifneq ($(SPLIT_FUNCTIONS), 0)
  DISASM_FUNC_SPLIT    = --split-functions $(BASE_DIR)/asm/functions/$*
endif

ifneq ($(PRINT_BOUNDARIES), 0)
  DISASM_EXTRA_PARAMS += --print-new-file-boundaries
endif



MAKE = make

DISASSEMBLER        ?= ./disasm.py

#### Files ####

BASE_DIR            := $(GAME)/$(VERSION)

# ROM image
BASE_ROM            := $(GAME)/$(GAME)_$(VERSION).z64

BASEROM_FILES       := $(wildcard $(BASE_DIR)/baserom/*)

# TODO: implement?
DISASM_LIST    	    := $(shell cat $(GAME)/tables/disasm_list.txt) \
                       $(shell [ -f $(BASE_DIR)/tables/disasm_list.txt ] && cat $(BASE_DIR)/tables/disasm_list.txt)

CSV_FILES           := $(wildcard $(GAME)/tables/*.csv)

.PHONY: all splitcsvs disasm clean downloadcsvs csvs
.DEFAULT_GOAL := all


#### Main commands ####

## Cleaning ##
clean:
	$(RM) -rf $(BASE_DIR)/asm $(BASE_DIR)/context

asmclean:
	$(RM) -rf $(BASE_DIR)/asm $(BASE_DIR)/context

## Extraction step
setup:
	./extract_baserom.py $(GAME) $(VERSION)

## Assembly generation
disasm: $(BASE_DIR)/asm/.disasm
	@echo "Disassembly done!"



all: disasm

disasm: splitcsvs

splitcsvs: $(CSV_FILES)

downloadcsvs:
	./tools/csvhelpers/download_csv_$(GAME).sh

csvs:
	$(MAKE) downloadcsvs
	$(MAKE) splitcsvs

#### Various Recipes ####
$(BASE_DIR)/tables/%.csv: $(GAME)/tables/%.csv
	./csvSplit.py $(GAME) $<
$(BASE_DIR)/tables/files_%.csv: $(GAME)/tables/%.*.csv
	./csvSplit.py $(GAME) $<



$(BASE_DIR)/asm/.disasm: $(BASEROM_FILES) $(CSV_FILES) $(DISASSEMBLER)
	$(DISASSEMBLER) --game $(GAME) --version $(VERSION) $(DISASM_VERBOSITY) $(DISASM_EXTRA_PARAMS) \
		--functions $(BASE_DIR)/tables/functions.csv \
		--default-banned --libultra-syms --hardware-regs --named-hardware-regs
	@touch $@


# Print target for debugging
print-% : ; $(info $* is a $(flavor $*) variable set to [$($*)]) @true
