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
DISASM_EXTRA_PARAMS    += --function-info $(GAME)/function_info/$(VERSION)_$*_function_info.csv
DISASM_EXTRA_PARAMS    += --custom-suffix _$(VERSION)
DISASM_EXTRA_PARAMS    += --sequential-label-names

OVL_DIS_EXTRA_PARAMS   ?=
ifeq ($(GAME), dnm)
  OVL_DIS_EXTRA_PARAMS += --reloc-separate
endif

DISASM_FUNC_SPLIT      = 
ifneq ($(SPLIT_FUNCTIONS), 0)
  DISASM_FUNC_SPLIT    = --split-functions $(BASE_DIR)/asm/functions/$*
endif

ifneq ($(PRINT_BOUNDARIES), 0)
  DISASM_EXTRA_PARAMS += --print-new-file-boundaries
endif



MAKE = make

DISASSEMBLER        ?= python3 -m spimdisasm.singleFileDisasm
OVL_DISASSEMBLER    ?= ./z64OvlDisasm.py

#### Files ####

BASE_DIR       := $(GAME)/$(VERSION)

# ROM image
BASE_ROM       := $(GAME)/$(GAME)_$(VERSION).z64

# ASM_DIRS       := $(shell find $(BASE_DIR)/asm/ -type d)

# S_FILES        := $(foreach dir,$(ASM_DIRS),$(wildcard $(dir)/*.s))

BASEROM_FILES       := $(wildcard $(BASE_DIR)/baserom/*)

DISASM_LIST    	    := $(shell cat $(GAME)/tables/disasm_list.txt) \
                       $(shell [ -f $(BASE_DIR)/tables/disasm_list.txt ] && cat $(BASE_DIR)/tables/disasm_list.txt)

CSV_FILES_ORIGINAL  := $(wildcard $(GAME)/tables/*.text.csv)

CSV_FILES           := $(CSV_FILES_ORIGINAL:$(GAME)/tables/%.text.csv=$(BASE_DIR)/tables/files_%.csv) \
                       $(BASE_DIR)/tables/functions.csv $(BASE_DIR)/tables/variables.csv

DISASM_TARGETS      := $(DISASM_LIST:%=$(BASE_DIR)/asm/text/%/.disasm)

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
	./decompress_baserom.py $(GAME) $(VERSION)
	./extract_baserom.py $(GAME) $(VERSION)

## Assembly generation
disasm: $(DISASM_TARGETS)
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
$(BASE_DIR)/tables/%.txt: $(GAME)/tables/%.csv
	./csvSplit.py $(GAME) $<
$(BASE_DIR)/tables/%.csv: $(GAME)/tables/%.csv
	./csvSplit.py $(GAME) $<
$(BASE_DIR)/tables/files_%.csv: $(GAME)/tables/%.*.csv
	./csvSplit.py $(GAME) $<



$(BASE_DIR)/asm/text/%/.disasm: $(BASE_DIR)/baserom/% $(BASE_DIR)/tables/variables.txt $(BASE_DIR)/tables/functions.txt $(BASE_DIR)/tables/files_%.csv
	$(RM) -rf $(BASE_DIR)/asm/text/$* $(BASE_DIR)/asm/data/$* $(BASE_DIR)/asm/functions/$* $(BASE_DIR)/context/$*.txt
	$(DISASSEMBLER) $< $(BASE_DIR)/asm/text/$* $(DISASM_VERBOSITY) --data-output $(BASE_DIR)/asm/data/$* $(DISASM_FUNC_SPLIT) \
		--file-splits $(BASE_DIR)/tables/files_$*.csv \
		--symbol-addrs $(BASE_DIR)/tables/variables.txt --symbol-addrs $(BASE_DIR)/tables/functions.txt \
		--constants $(GAME)/tables/constants.csv --constants $(BASE_DIR)/tables/constants_$*.csv \
		--save-context $(BASE_DIR)/context/$*.txt $(DISASM_EXTRA_PARAMS) \
		--default-banned --libultra-syms --hardware-regs --named-hardware-regs
	@touch $@


$(BASE_DIR)/asm/text/ovl_%/.disasm: $(BASE_DIR)/baserom/ovl_% $(BASE_DIR)/tables/variables.txt $(BASE_DIR)/tables/functions.txt
	$(RM) -rf $(BASE_DIR)/asm/text/ovl_$* $(BASE_DIR)/asm/data/ovl_$* $(BASE_DIR)/asm/functions/ovl_$* $(BASE_DIR)/context/ovl_$*.txt
	$(OVL_DISASSEMBLER) $< $(BASE_DIR)/asm/text/ovl_$* $(DISASM_VERBOSITY) --data-output $(BASE_DIR)/asm/data/ovl_$* $(DISASM_FUNC_SPLIT) \
		--file-splits $(BASE_DIR)/tables/files_ovl_$*.csv \
		--symbol-addrs $(BASE_DIR)/tables/variables.txt --symbol-addrs $(BASE_DIR)/tables/functions.txt \
		--constants $(GAME)/tables/constants.csv --constants $(BASE_DIR)/tables/constants_ovl_$*.csv \
		--file-addresses $(BASE_DIR)/tables/file_addresses.csv \
		--save-context $(BASE_DIR)/context/ovl_$*.txt $(DISASM_EXTRA_PARAMS) $(OVL_DIS_EXTRA_PARAMS) \
		--default-banned --libultra-syms --hardware-regs --named-hardware-regs
	@touch $@

# Print target for debugging
print-% : ; $(info $* is a $(flavor $*) variable set to [$($*)]) @true
