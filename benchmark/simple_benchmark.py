#!/usr/bin/env python3
"""
IPC Benchmark Runner
------------------
This script automates running benchmarks comparing shared memory and Unix domain socket
performance with various data sizes. It produces a comparison table and saves results to CSV.
"""

import subprocess
import time
import os
import sys
import csv
from typing import Dict, List, Any, Optional

# Create results directory if it doesn't exist
if not os.path.exists('results'):
    os.makedirs('results')

# Data sizes to test (in KB)
data_sizes = [1, 10, 100, 1000, 5000]

# Results will be stored here
results = {
    'shm': {},
    'socket': {}
}

def run_benchmark(mode: str, size: int) -> Dict[str, Optional[float]]:
    """
    Run benchmark for a specific mode and data size
    
    Args:
        mode: IPC mechanism ('shm' or 'socket')
        size: Data size in KB
    
    Returns:
        Dictionary with benchmark results
    """
    print(f"\n{'-' * 50}")
    print(f"Running {mode} benchmark with {size}KB of data")
    print(f"{'-' * 50}")
    
    # Build the server command
    server_cmd = f"./benchmark_server {mode} {size}"
    
    # Start server
    server_proc = subprocess.Popen(
        server_cmd, 
        shell=True,
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    
    # Give the server time to setup
    time.sleep(2)
    
    # Start client with renamed client script
    client_proc = subprocess.run(
        ["python3", "benchmark_client.py", mode], 
        capture_output=True, 
        text=True
    )
    
    # For shared memory, we need to terminate the server after client is done
    if mode == 'shm':
        server_proc.terminate()
        time.sleep(0.5)
    
    # Process results
    print(client_proc.stdout)
    
    # Extract metrics from client output
    duration_ms = None
    throughput = None
    
    for line in client_proc.stdout.splitlines():
        if "Duration:" in line:
            try:
                duration_ms = float(line.split(":")[1].strip().split()[0])
            except (ValueError, IndexError):
                pass
        elif "in" in line and "ms" in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == "in":
                    try:
                        duration_ms = float(parts[i+1])
                    except (ValueError, IndexError):
                        pass
        if "Throughput:" in line:
            parts = line.split()
            try:
                throughput = float(parts[1])
            except (ValueError, IndexError):
                pass
    
    return {
        'duration_ms': duration_ms,
        'throughput_MBps': throughput
    }

def format_value(value):
    """Format a value for display in the results table"""
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)

def print_results_table(results, data_sizes):
    """Print a formatted comparison table of benchmark results"""
    print("\n" + "=" * 80)
    print("BENCHMARK RESULTS")
    print("=" * 80)
    headers = [
        "Size (KB)", 
        "Shared Memory Time (ms)", 
        "Unix Socket Time (ms)", 
        "SHM Throughput (MB/s)", 
        "Socket Throughput (MB/s)"
    ]
    
    # Print headers
    header_row = f"{headers[0]:<10} | {headers[1]:<25} | {headers[2]:<25} | {headers[3]:<25} | {headers[4]:<25}"
    print(header_row)
    print("-" * 80)
    
    # Print data rows
    for size in data_sizes:
        shm_time = results['shm'][size]['duration_ms'] if size in results['shm'] else None
        socket_time = results['socket'][size]['duration_ms'] if size in results['socket'] else None
        shm_throughput = results['shm'][size]['throughput_MBps'] if size in results['shm'] else None
        socket_throughput = results['socket'][size]['throughput_MBps'] if size in results['socket'] else None
        
        row = (
            f"{size:<10} | "
            f"{format_value(shm_time):<25} | "
            f"{format_value(socket_time):<25} | "
            f"{format_value(shm_throughput):<25} | "
            f"{format_value(socket_throughput):<25}"
        )
        print(row)
    
def save_results_to_csv(results, data_sizes, filename):
    """Save benchmark results to a CSV file"""
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Size (KB)', 
            'Shared Memory Time (ms)', 
            'Unix Socket Time (ms)', 
            'SHM Throughput (MB/s)', 
            'Socket Throughput (MB/s)'
        ])
        
        for size in data_sizes:
            shm_time = results['shm'][size]['duration_ms'] if size in results['shm'] else None
            socket_time = results['socket'][size]['duration_ms'] if size in results['socket'] else None
            shm_throughput = results['shm'][size]['throughput_MBps'] if size in results['shm'] else None
            socket_throughput = results['socket'][size]['throughput_MBps'] if size in results['socket'] else None
            
            writer.writerow([
                size, 
                format_value(shm_time), 
                format_value(socket_time), 
                format_value(shm_throughput), 
                format_value(socket_throughput)
            ])

def main():
    """Main benchmark runner function"""
    print("Starting IPC benchmark comparison...")
    
    # Run benchmarks for both mechanisms with different data sizes
    for mode in ['shm', 'socket']:
        results[mode] = {}
        for size in data_sizes:
            result = run_benchmark(mode, size)
            results[mode][size] = result
    
    # Print comparison table
    print_results_table(results, data_sizes)
    
    # Save results to CSV
    csv_filename = 'results/benchmark_results.csv'
    save_results_to_csv(results, data_sizes, csv_filename)
    
    print(f"\nBenchmark complete! Results saved to {csv_filename}")
    
if __name__ == "__main__":
    main()
