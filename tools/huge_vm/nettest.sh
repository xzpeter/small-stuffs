for i in {1..8}; do
	port=1000${i}
	if (( $i % 2 == 0 )); then
		ip=192.168.1.11
	else
		ip=192.168.1.11
	fi
	netperf -H $ip -p $port -l 10000 &
done

echo "Press any key to stop"
read

pkill --signal SIGINT -f netperf
