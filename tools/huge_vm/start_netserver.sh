for port in {10001..10008}; do
	netserver -p $port
done
