MAKEFLAGS += --no-builtin-rules

# Build options can either be changed by modifying the makefile, or by building with 'make SETTING=value'

GAME                   ?= oot
VERSION                ?= ne0
# if SPLIT_FUNCTIONS is non-zero, the disassembler will try to split functions and rodata
SPLIT_FUNCTIONS        ?= 0


DISASM_VERBOSITY       ?= -q
DISASM_EXTRA_PARAMS    ?=

DISASM_FUNC_SPLIT      = 
ifneq ($(SPLIT_FUNCTIONS), 0)
  DISASM_FUNC_SPLIT    = --split-functions $(BASE_DIR)/asm/functions/$*
endif



MAKE = make

DISASSEMBLER        ?= ./py_mips_disasm/simpleDisasm.py
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

.PHONY: all splitcsvs disasm clean
.DEFAULT_GOAL := all


#### Main commands ####

## Cleaning ##
clean:
	$(RM) -rf $(BASE_DIR)/asm $(BASE_DIR)/context

asmclean:
	$(RM) -rf $(BASE_DIR)/asm $(BASE_DIR)/context

## Extraction step
setup:
#	$(MAKE) -C tools
	./extract_baserom.py $(GAME) $(VERSION)

## Assembly generation
disasm: $(DISASM_TARGETS)
	@echo "Disassembly done!"



all: disasm

disasm: splitcsvs

splitcsvs: $(CSV_FILES)

#### Various Recipes ####
$(BASE_DIR)/tables/%.csv: $(GAME)/tables/%.csv
	./csvSplit.py $(GAME) $<
$(BASE_DIR)/tables/files_%.csv: $(GAME)/tables/%.*.csv
	./csvSplit.py $(GAME) $<



$(BASE_DIR)/asm/text/%/.disasm: $(BASE_DIR)/baserom/% $(BASE_DIR)/tables/variables.csv $(BASE_DIR)/tables/functions.csv $(BASE_DIR)/tables/files_%.csv
	$(RM) -rf $(BASE_DIR)/asm/text/$* $(BASE_DIR)/asm/data/$* $(BASE_DIR)/asm/functions/$* $(BASE_DIR)/context/$*.txt
	$(DISASSEMBLER) $< $(BASE_DIR)/asm/text/$* $(DISASM_VERBOSITY) --data-output $(BASE_DIR)/asm/data/$* $(DISASM_FUNC_SPLIT) \
		--file-splits $(BASE_DIR)/tables/files_$*.csv \
		--variables $(BASE_DIR)/tables/variables.csv --functions $(BASE_DIR)/tables/functions.csv \
		--constants $(GAME)/tables/constants.csv --constants $(BASE_DIR)/tables/constants_$*.csv \
		--save-context $(BASE_DIR)/context/$*.txt $(DISASM_EXTRA_PARAMS)
	@touch $@


$(BASE_DIR)/asm/text/ovl_%/.disasm: $(BASE_DIR)/baserom/ovl_% $(BASE_DIR)/tables/variables.csv $(BASE_DIR)/tables/functions.csv
	$(RM) -rf $(BASE_DIR)/asm/text/ovl_$* $(BASE_DIR)/asm/data/ovl_$* $(BASE_DIR)/asm/functions/ovl_$* $(BASE_DIR)/context/ovl_$*.txt
	$(OVL_DISASSEMBLER) $< $(BASE_DIR)/asm/text/ovl_$* $(DISASM_VERBOSITY) --data-output $(BASE_DIR)/asm/data/ovl_$* $(DISASM_FUNC_SPLIT) \
		--file-splits $(BASE_DIR)/tables/files_ovl_$*.csv \
		--variables $(BASE_DIR)/tables/variables.csv --functions $(BASE_DIR)/tables/functions.csv \
		--constants $(GAME)/tables/constants.csv --constants $(BASE_DIR)/tables/constants_ovl_$*.csv \
		--file-addresses $(BASE_DIR)/tables/file_addresses.csv \
		--save-context $(BASE_DIR)/context/ovl_$*.txt $(DISASM_EXTRA_PARAMS)
	@touch $@
