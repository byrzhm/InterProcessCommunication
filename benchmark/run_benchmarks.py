#!/usr/bin/env python3
import subprocess
import time
import matplotlib.pyplot as plt
import numpy as np
import os

# Ensure the output directory exists
if not os.path.exists('results'):
    os.makedirs('results')

# Data sizes to test (in KB)
data_sizes = [1, 10, 100, 1000, 5000, 10000]  # 1KB to 10MB
results = {
    'shm': {'sizes': [], 'times': []},
    'socket': {'sizes': [], 'times': []}
}

def run_benchmark(mode, size):
    print(f"\n{'=' * 50}")
    print(f"Running {mode.upper()} benchmark with {size}KB data")
    print(f"{'=' * 50}")
    
    # Start the server
    server_proc = subprocess.Popen(
        ['../benchmark/benchmark_server', mode, str(size)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Give the server time to start
    time.sleep(2)
    
    # Run client with the renamed benchmark_client.py
    client_proc = subprocess.Popen(
        ['python3', '../benchmark/benchmark_client.py', mode],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Get client output
    client_output, client_error = client_proc.communicate()
    
    print("Client output:")
    print(client_output)
    
    if client_error:
        print("Client error:")
        print(client_error)
    
    # For shared memory, we need to terminate the server process after client is done
    if mode == 'shm':
        # Give it a moment for the client to read data
        time.sleep(1)
        # Kill the server process
        server_proc.terminate()
    
    # Get server output
    server_output, server_error = server_proc.communicate()
    
    print("Server output:")
    print(server_output)
    
    if server_error:
        print("Server error:")
        print(server_error)
    
    # Parse the results
    duration = None
    for line in client_output.splitlines():
        if "in" in line and "ms" in line:
            try:
                duration = float(line.split("in")[1].split("ms")[0].strip())
            except:
                pass
    
    return duration

# Run benchmarks for both mechanisms with different data sizes
for mode in ['shm', 'socket']:
    for size in data_sizes:
        time_taken = run_benchmark(mode, size)
        if time_taken is not None:
            results[mode]['sizes'].append(size)
            results[mode]['times'].append(time_taken)

# Plot the results
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.plot(results['shm']['sizes'], results['shm']['times'], 'bo-', label='Shared Memory')
plt.plot(results['socket']['sizes'], results['socket']['times'], 'ro-', label='Unix Domain Socket')
plt.xlabel('Data Size (KB)')
plt.ylabel('Time (ms)')
plt.title('IPC Performance Comparison (Time)')
plt.grid(True)
plt.legend()

plt.subplot(1, 2, 2)
shm_throughput = [size / (time / 1000) / 1024 for size, time in zip(results['shm']['sizes'], results['shm']['times'])]
socket_throughput = [size / (time / 1000) / 1024 for size, time in zip(results['socket']['sizes'], results['socket']['times'])]

plt.plot(results['shm']['sizes'], shm_throughput, 'bo-', label='Shared Memory')
plt.plot(results['socket']['sizes'], socket_throughput, 'ro-', label='Unix Domain Socket')
plt.xlabel('Data Size (KB)')
plt.ylabel('Throughput (MB/s)')
plt.title('IPC Performance Comparison (Throughput)')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.savefig('results/ipc_benchmark_comparison.png')

# Save results to a CSV file
with open('results/benchmark_results.csv', 'w') as f:
    f.write('Size (KB),Shared Memory (ms),Unix Socket (ms),Shared Memory (MB/s),Unix Socket (MB/s)\n')
    for i, size in enumerate(data_sizes):
        if i < len(results['shm']['times']) and i < len(results['socket']['times']):
            f.write(f"{size},{results['shm']['times'][i]},{results['socket']['times'][i]},{shm_throughput[i]},{socket_throughput[i]}\n")

print("\nBenchmarks complete! Results saved to results/benchmark_results.csv and results/ipc_benchmark_comparison.png")
