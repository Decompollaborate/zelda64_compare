MAKEFLAGS += --no-builtin-rules

# Build options can either be changed by modifying the makefile, or by building with 'make SETTING=value'

GAME     ?= oot
VERSION  ?= ne0

MAKE = make

DISASSEMBLER    ?= py-mips-disasm/simpleDisasm.py

#### Files ####

BASE_DIR       := $(GAME)

# ROM image
BASE_ROM       := $(BASE_DIR)/$(GAME)_$(VERSION).z64

ASM_DIRS       := $(shell find $(BASE_DIR)/$(VERSION)/asm/ -type d)

S_FILES        := $(foreach dir,$(ASM_DIRS),$(wildcard $(dir)/*.s))

BASEROM_FILES  := $(wildcard $(BASE_DIR)/$(VERSION)/baserom/*)


.PHONY: all splitcsvs disasm clean
.DEFAULT_GOAL := all


#### Main commands ####

## Cleaning ##
clean:
	$(RM) -rf $(BASE_DIR)/$(VERSION)/asm $(BASE_DIR)/$(VERSION)/context

## Extraction step
setup:
	$(MAKE) -C tools
	./extract_baserom.py $(VERSION) $(BASE_ROM)

## Assembly generation
disasm: $(DISASM_TARGETS)
	@echo "Disassembly done!"



all: disasm

disasm: splitcsvs

splitcsvs: $(BASE_DIR)/$(VERSION)/tables/%.csv


#### Various Recipes ####
$(BASE_DIR)/$(VERSION)/tables/%.csv: $(BASE_DIR)/tables/%.csv
	./csvSplit.py $(GAME) $<



$(BASE_DIR)/asm/text/%/.disasm: $(BASE_DIR)/baserom/% $(BASE_DIR)/tables/variables.csv $(BASE_DIR)/tables/functions.csv $(BASE_DIR)/tables/files_%.csv
	$(RM) -rf $(BASE_DIR)/asm/text/$* $(BASE_DIR)/asm/data/$* $(BASE_DIR)/context/$*.txt
	$(DISASSEMBLER) $< $(BASE_DIR)/asm/text/$* -q --data-output $(BASE_DIR)/asm/data/$* --variables $(BASE_DIR)/tables/variables.csv --functions $(BASE_DIR)/tables/functions.csv --file-splits $(BASE_DIR)/tables/files_$*.csv  --save-context $(BASE_DIR)/context/$*.txt --functions $(BASE_DIR)/tables/functions_$*.csv --variables $(BASE_DIR)/tables/variables_$*.csv --constants $(BASE_DIR)/tables/constants_$*.csv
	@touch $@
