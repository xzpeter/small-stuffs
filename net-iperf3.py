#!/usr/bin/env python3

import subprocess
import argparse
import json
import sys

BASE_PORT = 5201

def start_server_processes(num_servers):
    server_processes = []
    for i in range(num_servers):
        port = str(BASE_PORT + i)
        server_process = subprocess.Popen(
            ['iperf3', '-s', '-J', '-p', port], stdout=subprocess.PIPE)
        server_processes.append(server_process)
        print(f"Server {i} iperf3 process created (port {port})")
    return server_processes

def start_client_processes(host, num_clients, duration):
    client_processes = []
    for i in range(num_clients):
        port = str(BASE_PORT + i)
        client_process = subprocess.Popen(
            ['iperf3', '-c', host, '-J', '-p', port, '-t', str(duration)],
            stdout=subprocess.PIPE)
        client_processes.append(client_process)
        print(f"Client {i} iperf3 process created (port {port})")
    print(f"Running the test (duration: {duration} seconds)")
    return client_processes

def parse_bandwidth(json_output):
    results = json.loads(json_output)
    # Unit is Gbps
    return results['end']['sum_sent']['bits_per_second'] / 1e9

def main():
    parser = argparse.ArgumentParser(
        description="Starts iperf3 server/client processes and reports summary bandwidth.")
    parser.add_argument('-d', dest='duration', default=1,
                        help="Duration of the test (client side only)")
    parser.add_argument('-s', action='store_true', help="Start in server mode")
    parser.add_argument('-c', dest='host', help="Start in client mode (with HOST as target)")
    parser.add_argument('-N', dest='num_processes', type=int, default=1,
                        help="Number of iperf3 server/client processes to start")
    args = parser.parse_args()

    if args.s:
        server_processes = start_server_processes(args.num_processes)
        for process in server_processes:
            # Server side ignores all things
            _, _ = process.communicate()
    elif args.host:
        client_processes = start_client_processes(
            args.host, args.num_processes, args.duration)
        total = count = 0
        for process in client_processes:
            output, _ = process.communicate()
            bandwidth = parse_bandwidth(output)
            print(f"Client {count} bandwidth: {bandwidth:.2f} Gbps ({bandwidth/8:.2f} GBps)")
            count += 1
            total += bandwidth
        print(f"Total bandwidth: {total:.2f} Gbps ({total/8:.2f} GBps)")
    else:
        parser.print_help()
        sys.exit(0)

if __name__ == "__main__":
    main()
