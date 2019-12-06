#!/usr/bin/bash

sed -i 's/\[[^\[].*\]//g; s/<strong>[^<]*<\/strong>//g; s/<\![^<]*>//g' $@
