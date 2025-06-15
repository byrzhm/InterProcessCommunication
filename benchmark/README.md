# IPC Benchmark: Shared Memory vs Unix Domain Socket

This project benchmarks two Inter-Process Communication (IPC) mechanisms:
1. POSIX Shared Memory
2. Unix Domain Sockets

## Components

- `benchmark_server.cpp`: C++ server that can use both IPC mechanisms
- `benchmark_client.py`: Python client that communicates with the server
- `simple_benchmark.py`: Script that runs benchmarks with both mechanisms and various data sizes
- `run_benchmarks.py`: Advanced benchmark script that generates graphical comparisons

## Usage

### Compile the server

```bash
cd benchmark
make
```

### Running individual benchmarks

For shared memory:
```bash
# Terminal 1
./benchmark_server shm 1000   # Use shared memory with 1000KB data

# Terminal 2
python3 benchmark_client.py shm
```

For Unix domain sockets:
```bash
# Terminal 1
./benchmark_server socket 1000   # Use Unix domain socket with 1000KB data

# Terminal 2
python3 benchmark_client.py socket
```

### Running complete benchmark comparison

```bash
./simple_benchmark.py
```

The results will be saved in the `results` directory.

## Benchmark Results

The benchmarks compare:
- Transfer time for different data sizes
- Throughput (MB/s) for different data sizes

### Performance Comparison

Based on the benchmark results, here are the key findings:

1. **Small Data Transfer** (1-10KB):
   - Shared Memory is faster for small data transfers
   - For 1KB data: Shared Memory is approximately 3x faster than Unix Domain Socket
   - For 10KB data: Shared Memory is approximately 5x faster than Unix Domain Socket

2. **Medium Data Transfer** (100KB):
   - Shared Memory maintains a significant advantage
   - Shared Memory is approximately 3x faster than Unix Domain Socket

3. **Large Data Transfer** (1000KB-5000KB):
   - The performance gap narrows for large data transfers
   - For 1000KB data: Shared Memory is about 1.4x faster than Unix Domain Socket
   - For 5000KB data: Shared Memory is only marginally faster than Unix Domain Socket

### Conclusions

- **Shared Memory** excels at all data sizes but has the biggest advantage for small to medium data transfers.
- **Unix Domain Socket** performs relatively better as the data size increases, nearly matching Shared Memory for large transfers.
- **Overhead** is more significant for Unix Domain Sockets with smaller data sizes due to socket connection establishment and system call overhead.

### When to Use Each Mechanism

- **Use Shared Memory** when:
  - Maximum performance is critical
  - Transferring small to medium amounts of data frequently
  - Low latency is essential
  - Processes have a well-defined shared data structure

- **Use Unix Domain Sockets** when:
  - You need a bidirectional communication channel
  - Connection management is important (client/server model)
  - Message-oriented communication is preferred
  - Transferring larger data or streaming data
  - You need to communicate between processes that start and stop independently
