# Script from Jason Wang to initiate multiple netperf instances.

session=$1
shift 1

if echo $@ | grep -q "\-l [[:digit:]]*"
then
    l=`echo $@ | grep -o "\-l [[:digit:]]*" | awk '{print $2}'`
else
    l=10
fi

for i in $(seq $session)
do
    netperf -D 1 $@ &
done >result 2>debug
sleep $l
pkill netperf

# post processing
# Examine how many sessions were launched
nsession=$(grep MIGRATE result | wc -l)
if [ $nsession -ne $session ]
then
    echo the expected sessions could not be met, expect $session get $nsession
    echo $@
    exit 2
fi

# Track the last netperf instance's start
start=$(less result | grep -n MIGRATE | tail -n 1 | awk -F ':' '{print $1}')

# How many lines of result file
nlines=$(wc -l result | awk '{print $1}')
# We only need from line $start to $end
tail -n $(($nlines-$start)) result > result2

# Track the first netperf instance's end
end=$(less result2 | grep -En "Recv|Local" | head -n 1 | awk -F ':' '{print $1}')
head -n $(($end-1)) result2 > result3

# verify whether we could test with this parallism
nresult=$(wc -l result3 | awk '{print $1}')
if [ $nresult -lt $session ]
then
    echo "We couldn't expect this parallism, expect $session get $nresult"
    exit 2
fi

# remove the noise from head
niteration=$(($nresult/$session))
tail -n $(($session*$niteration)) result3 > final_result

# calculate the final result
result=0
for this in $(less final_result | awk '{print $3}')
do
    result=$(echo $result+$this | bc)
done

result=$(echo "scale=2; $result/$niteration" | bc)
echo $result
