#!/bin/bash

grep "\w\+ *(" *.c | grep -v csx | grep "\w\+ *(" --color
