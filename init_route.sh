#!/bin/bash

action=$1

# gateway=192.168.1.1
# try to find gateway. This is smarter than setting it all static.
gateway=$(netstat -nr | grep default | grep -v ppp | awk '{print $2}')
target_list="192.168.0.0/16"

for target in $target_list; do
	case $action in
	add)
		sudo route delete $target &> /dev/null
		sudo route add $target $gateway &> /dev/null;;
	delete|del|remove)
		sudo route delete $target &> /dev/null;;
	*) 
		echo "args errro"; exit 1 ;;
	esac
done
