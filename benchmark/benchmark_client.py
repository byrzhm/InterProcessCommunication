#!/usr/bin/env python3
"""
IPC Benchmark Client
-------------------
This module provides client implementations for benchmarking different IPC mechanisms:
1. Shared Memory
2. Unix Domain Sockets

It measures read/receive performance and reports throughput statistics.
"""

import argparse
import mmap
import os
import socket
import struct
import time
from typing import Optional, Tuple, Dict, Any, Union

# Constants
SHM_NAME = '/benchmark_shared_memory'
SHM_SIZE = 10 * 1024 * 1024  # 10MB
SOCKET_PATH = "/tmp/benchmark_unix_socket"
BUFFER_SIZE = 8192  # Socket receive buffer size

class BenchmarkResult:
    """Class to store and report benchmark results"""
    
    def __init__(self, data_size: int, duration_ms: float, data: Union[bytes, bytearray, None] = None):
        self.data_size = data_size
        self.duration_ms = duration_ms
        self.data = data
        
    @property
    def data_size_kb(self) -> float:
        """Data size in KB"""
        return self.data_size / 1024
        
    @property
    def throughput_mbps(self) -> float:
        """Throughput in MB/s"""
        return (self.data_size_kb / 1024) / (self.duration_ms / 1000) if self.duration_ms > 0 else 0
    
    def report(self) -> None:
        """Print benchmark results"""
        print(f"Data size: {self.data_size_kb:.2f} KB")
        print(f"Duration: {self.duration_ms:.2f} ms")
        print(f"Throughput: {self.throughput_mbps:.2f} MB/s")
        if self.data:
            print(f"First few bytes of received data: {self.data[:20]}")


class SharedMemoryClient:
    """Client implementation using POSIX shared memory"""
    
    def __init__(self, shm_name: str = SHM_NAME, shm_size: int = SHM_SIZE):
        self.shm_name = shm_name
        self.shm_size = shm_size
        self.shm_path = f"/dev/shm{shm_name}"
        
    def wait_for_shm(self, timeout_sec: float = 10.0) -> bool:
        """Wait for shared memory to be created"""
        start_time = time.time()
        while not os.path.exists(self.shm_path):
            if time.time() - start_time > timeout_sec:
                print(f"Timeout waiting for shared memory at {self.shm_path}")
                return False
            print("Waiting for shared memory to be created...")
            time.sleep(0.1)
        return True
        
    def read_data(self) -> BenchmarkResult:
        """Read data from shared memory and measure performance"""
        print(f"Starting shared memory benchmark...")
        
        if not self.wait_for_shm():
            return BenchmarkResult(0, 0, None)
        
        start_time = time.time()
        
        try:
            with open(self.shm_path, 'r+b') as f:
                with mmap.mmap(f.fileno(), self.shm_size, access=mmap.ACCESS_READ) as shm:
                    # Read data size (first 8 bytes)
                    data_size = struct.unpack('Q', shm[0:8])[0]
                    
                    # Read data
                    data = shm[8:8+data_size]
        except Exception as e:
            print(f"Error reading shared memory: {e}")
            return BenchmarkResult(0, 0, None)
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000  # Convert to milliseconds
        
        result = BenchmarkResult(len(data), duration_ms, data)
        print(f"Shared memory read complete. Read {result.data_size_kb:.2f} KB in {result.duration_ms:.2f} ms")
        print(f"Throughput: {result.throughput_mbps:.2f} MB/s")
        
        return result


class UnixSocketClient:
    """Client implementation using Unix domain sockets"""
    
    def __init__(self, socket_path: str = SOCKET_PATH, buffer_size: int = BUFFER_SIZE):
        self.socket_path = socket_path
        self.buffer_size = buffer_size
        self.client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        
    def connect(self, timeout_sec: float = 5.0) -> bool:
        """Connect to the server"""
        print(f"Connecting to socket at {self.socket_path}...")
        self.client.settimeout(timeout_sec)
        try:
            self.client.connect(self.socket_path)
            return True
        except (ConnectionRefusedError, FileNotFoundError) as e:
            print(f"Connection failed: {e}")
            print("Make sure the server is running.")
            return False
        finally:
            # Reset timeout to blocking mode
            self.client.settimeout(None)
            
    def read_data(self) -> BenchmarkResult:
        """Read data from socket and measure performance"""
        print(f"Starting Unix domain socket benchmark...")
        
        if not self.connect():
            return BenchmarkResult(0, 0, None)
        
        try:
            start_time = time.time()
            
            # Receive data size (first 8 bytes)
            data_size_bytes = self.client.recv(8)
            if len(data_size_bytes) != 8:
                raise ValueError("Failed to receive data size")
                
            data_size = struct.unpack('Q', data_size_bytes)[0]
            
            # Receive data in chunks
            data = bytearray()
            bytes_received = 0
            
            while bytes_received < data_size:
                chunk = self.client.recv(min(self.buffer_size, data_size - bytes_received))
                if not chunk:
                    break  # Connection closed by server
                data.extend(chunk)
                bytes_received += len(chunk)
            
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000  # Convert to milliseconds
            
            result = BenchmarkResult(len(data), duration_ms, data)
            print(f"Unix domain socket read complete. Read {result.data_size_kb:.2f} KB in {result.duration_ms:.2f} ms")
            print(f"Throughput: {result.throughput_mbps:.2f} MB/s")
            
            return result
            
        except Exception as e:
            print(f"Error receiving data: {e}")
            return BenchmarkResult(0, 0, None)
        finally:
            self.client.close()


def main():
    """Main entry point for the benchmark client"""
    parser = argparse.ArgumentParser(
        description='Benchmark client for IPC mechanisms',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 benchmark_client.py shm     # Benchmark using shared memory
  python3 benchmark_client.py socket  # Benchmark using Unix domain socket
        """
    )
    parser.add_argument('mode', choices=['shm', 'socket'], 
                        help='IPC mechanism to benchmark')
    
    args = parser.parse_args()
    
    if args.mode == 'shm':
        client = SharedMemoryClient()
        result = client.read_data()
    elif args.mode == 'socket':
        client = UnixSocketClient()
        result = client.read_data()
    else:
        print(f"Unknown mode: {args.mode}")
        return
    
    # Result is already reported in the read_data methods


if __name__ == "__main__":
    main()
