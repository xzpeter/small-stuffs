#!/bin/bash

hugepage=true
postcopy=true
hugepagesize=2M
image=~/images/default.qcow2
bin=~/git/qemu/bin/qemu-system-x86_64
mem=1T

param=""
if [[ -n "$1" ]]; then
	param="-incoming tcp:0.0.0.0:12345"
	#param="-incoming unix:/tmp/peter.sock"
	port=5556
	mon=6667
else
	port=5555
	mon=6666
fi

if $hugepage; then
	param="$param -object memory-backend-memfd,id=mem,size=${mem},hugetlb=on,hugetlbsize=${hugepagesize}"
	param="$param -numa node,memdev=mem"
	#param="$param -mem-prealloc"
fi

if $postcopy; then
	param="$param -global migration.x-postcopy-ram=on"
	param="$param -global migration.max-postcopy-bandwidth=0"
else
	param="$param -global migration.x-multifd=on"
	param="$param -global migration.multifd-channels=8"
fi

sudo $bin -M q35,accel=kvm -smp 128 -m ${mem} -msg timestamp=on \
     -name peter-vm,debug-threads=on \
     -global migration.x-max-bandwidth=0 \
     -trace enable=runstate_set \
     -nographic -monitor telnet::${mon},server,nowait \
     -netdev user,id=net0,hostfwd=tcp::${port}-:22 \
     -device virtio-net-pci,netdev=net0 \
     $param $image
