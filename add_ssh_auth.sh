#!/bin/bash

rsa_file=~/.ssh/id_rsa.pub

function usage ()
{
	cat <<EOF
usage: $0 [remote_machine]
e.g. $0 root@relay
EOF
	exit 0
}

if [ ! -f $rsa_file ]; then
	echo "seems don't have a ssh rsa public key... generating pairs..."
	ssh-keygen
fi

if [ -z $1 ]; then
	usage
fi

cat $rsa_file | ssh $@ "mkdir -p ~/.ssh/; cat >> ~/.ssh/authorized_keys"
