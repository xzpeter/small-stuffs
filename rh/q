#!/bin/bash

qemu_bin=""

prog_name="$0"
qemu_bin_x86=x86_64-softmmu/qemu-system-x86_64
qemu_bin_list="$qemu_bin_x86 bin/$qemu_bin_x86
               $(which qemu-system-x86_64 2>/dev/null)"
image=~/images/default.qcow2
mem_size=8G
# Allow to plug in extra mem
max_mem_size=16G
ncpu=$(nproc)

output()
{
    echo "==> $@"
}

usage()
{
    cat <<EOF

usage $prog_name [extra QEMU cmdlines...]

This script boot a QEMU virtual machine that support below things:

   - $ncpu vCPU
   - memory size $mem_size, max mem size $max_mem_size
   - SSH forward to guest port 22 at local port 5555
   - HMP telnet at local port 6666
   - GDB server at local port 1234
   - QMP unix socket at /tmp/peter.qmp
     (Connect use e.g.: ./qmp-shell -pv /tmp/peter.qmp)
   - Device 1: virtio-net-pci, with slirp
   - Device 2: virtio-blk-pci, with root image $image
   - PCI buses 03/04 (pcie.3/pcie.4) can be hot plugged

EOF
    exit 1
}

locate_qemu_binary()
{
    local bin

    for bin in $qemu_bin_list; do
        if [[ -x $bin ]]; then
            qemu_bin=$bin
            break
        fi
    done

    if [[ -z "$qemu_bin" ]]; then
        output "No QEMU binary found"
        exit 1
    fi

    output "QEMU binary to use: $qemu_bin"
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    usage
fi

locate_qemu_binary
$qemu_bin -M q35,kernel-irqchip=split,nvdimm=on -accel kvm -s \
          -m $mem_size,slots=4,maxmem=$max_mem_size \
          -name peter-vm,debug-threads=on -msg timestamp=on \
          -nographic -cpu host -smp $ncpu \
          -device intel-iommu \
          -global migration.x-max-bandwidth=104857600 \
          -global migration.x-events=on \
          -global migration.x-postcopy-ram=on \
          -monitor telnet:localhost:6666,server,nowait \
          -qmp unix:/tmp/peter.qmp,server,nowait \
          -device ioh3420,id=pcie.1,chassis=1 \
          -netdev user,id=net0,hostfwd=tcp::5555-:22 \
          -device virtio-net-pci,netdev=net0,bus=pcie.1 \
          -device ioh3420,id=pcie.2,chassis=2 \
          -drive file=$image,id=drive0,if=none,aio=io_uring \
          -device virtio-blk-pci,drive=drive0,bus=pcie.2 \
          -device ioh3420,id=pcie.3,chassis=3 \
          -device virtio-balloon,bus=pcie.3 \
          -device ioh3420,id=pcie.4,chassis=4 \
          -device e1000e \
          "$@"
