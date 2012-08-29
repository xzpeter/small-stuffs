# This is a very simple-use Makefile for C source codes using GCC

###### FEATURES: ######
# 1. auto update header dependencies
#    (so that after header modifications, target will also be rebuild when make)
# 2. arrange your source code in any directory structure
#    (just put all include files into INCLUDE_DIR)
# 3. easy to use
#    (follow the STEPS)

###### STEPS: ######
# 1. set EXEC as output file name
# 2. set INCLUDE_DIR to the directory with all the *.h files
# 3. write all *.c files and put them in anywhere in the current directory
# 4. try make it!

# Here are the two variables you have to set before you try MAKE
EXEC=main
INCLUDE_DIR=includes/

CC=gcc
SRC_FILES=$(shell find -name "*.c")
OBJ_FILES=$(SRC_FILES:.c=.o)
DEP_FILES=$(SRC_FILES:.c=.d)

default: $(EXEC)
.PHONY: clean

%.d: %.c
	@$(CC) -o $@ -MM -I $(INCLUDE_DIR) $<

CFLAGS=-g -I$(INCLUDE_DIR)

$(EXEC): $(OBJ_FILES)

clean:
	@rm -f $(OBJ_FILES) $(EXEC) $(DEP_FILES)

sinclude $(DEP_FILES)
