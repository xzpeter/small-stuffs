#!/bin/bash

qemu_bin=""

prog_name="$0"
qemu_bin_x86=./qemu-system-x86_64
qemu_bin_list="$qemu_bin_x86 bin/$qemu_bin_x86
               $(which qemu-system-x86_64 2>/dev/null)"
image=~/images/default.qcow2
nvdimm_image=~/images/nvdimm1
mem_size=6G
# Allow to plug in extra mem
max_mem_size=16G
ncpu=$(nproc)

ssh_port=5555
hmp_port=6666
qmp_index=1
gdb_port=1234

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

if [[ "$@" == *"-incoming"* ]]; then
    output "Booting a destination QEMU..."
    ssh_port=$(( ssh_port + 1 ))
    hmp_port=$(( hmp_port + 1 ))
    gdb_port=$(( gdb_port + 1 ))
    qmp_index=$(( qmp_index + 1 ))
fi

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
$qemu_bin -M q35,kernel-irqchip=split -accel kvm \
          -gdb tcp::${gdb_port} \
          -m $mem_size,slots=4,maxmem=$max_mem_size \
          -name peter-vm,debug-threads=on -msg timestamp=on \
          -nographic -cpu host -smp $ncpu \
          -device intel-iommu \
          -global migration.x-max-bandwidth=1M \
          -global migration.x-events=on \
          -global migration.x-postcopy-ram=on \
          -global migration.x-postcopy-preempt=on \
          -monitor telnet:localhost:${hmp_port},server,nowait \
          -qmp unix:/tmp/peter.qmp${qmp_index},server,nowait \
          -device ioh3420,id=pcie.1,chassis=1 \
          -netdev user,id=net0,hostfwd=tcp::${ssh_port}-:22 \
          -device virtio-net-pci,netdev=net0,bus=pcie.1 \
          -device ioh3420,id=pcie.2,chassis=2 \
          -drive file=$image,id=drive0,if=none,aio=io_uring \
          -device virtio-blk-pci,drive=drive0,bus=pcie.2 \
          -device ioh3420,id=pcie.3,chassis=3 \
          -device virtio-balloon,bus=pcie.3 \
          -device ioh3420,id=pcie.4,chassis=4 \
          "$@"
