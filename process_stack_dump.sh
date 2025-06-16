prog=$0
pid=$1

check_app()
{
    app=$1
    package=$2

    if ! which $app &> /dev/null; then
        echo "Binary $app is missing, please install $package"
        exit 1
    fi
}

if [[ -z "$pid" ]]; then
    echo "usage: $prog <pid>"
    exit 1
fi

check_app eu-stack elfutils
check_app pstree psmisc

echo "======================="
echo "Dumping userspace stack"
echo "======================="

eu-stack -p $pid

echo "======================="
echo "Dumping kernel stack"
echo "======================="

pstree -p $pid | grep -o "([0-9]\+)" | sed 's/[()]//g' |
    while read tid; do
        echo "TID $tid stack:"
        cat /proc/$tid/stack
        echo
    done
