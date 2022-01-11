MAKEFLAGS += --no-builtin-rules

# Build options can either be changed by modifying the makefile, or by building with 'make SETTING=value'

GAME     ?= oot
VERSION  ?= ne0

MAKE = make

DISASSEMBLER    ?= py_mips_disasm/simpleDisasm.py

#### Files ####

BASE_DIR       := $(GAME)/$(VERSION)

# ROM image
BASE_ROM       := $(GAME)/$(GAME)_$(VERSION).z64

ASM_DIRS       := $(shell find $(BASE_DIR)/asm/ -type d)

S_FILES        := $(foreach dir,$(ASM_DIRS),$(wildcard $(dir)/*.s))

BASEROM_FILES  := $(wildcard $(BASE_DIR)/baserom/*)

DISASM_TARGETS := $(shell sed -r 's/(.+)/$(GAME)\/$(VERSION)\/asm\/text\/\1\/.disasm/' $(GAME)/tables/disasm_list.txt)

.PHONY: all splitcsvs disasm clean
.DEFAULT_GOAL := all


#### Main commands ####

## Cleaning ##
clean:
	$(RM) -rf $(BASE_DIR)/asm $(BASE_DIR)/context

## Extraction step
setup:
	$(MAKE) -C tools
	./extract_baserom.py $(VERSION) $(BASE_ROM)

## Assembly generation
disasm: $(DISASM_TARGETS)
	@echo "Disassembly done!"



all: disasm

disasm: splitcsvs

# ??
#splitcsvs: $(BASE_DIR)/tables/%.csv


#### Various Recipes ####
$(BASE_DIR)/tables/%.csv: $(GAME)/tables/%.csv
	./csvSplit.py $(GAME) $<



$(BASE_DIR)/asm/text/%/.disasm: $(BASE_DIR)/baserom/% $(BASE_DIR)/tables/variables.csv $(BASE_DIR)/tables/functions.csv $(BASE_DIR)/tables/files_%.csv
	$(RM) -rf $(BASE_DIR)/asm/text/$* $(BASE_DIR)/asm/data/$* $(BASE_DIR)/context/$*.txt
	$(DISASSEMBLER) $< $(BASE_DIR)/asm/text/$* -q --data-output $(BASE_DIR)/asm/data/$* --variables $(BASE_DIR)/tables/variables.csv --functions $(BASE_DIR)/tables/functions.csv --constants $(GAME)/tables/constants.csv --file-splits $(BASE_DIR)/tables/files_$*.csv  --save-context $(BASE_DIR)/context/$*.txt --constants $(BASE_DIR)/tables/constants_$*.csv
	@touch $@
