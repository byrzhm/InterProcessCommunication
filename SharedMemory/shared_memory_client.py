import mmap
import struct
import os

SHM_NAME = '/my_shared_memory'
SHM_SIZE = 1024 * 1024

# In Linux, POSIX shared memory objects are in /dev/shm directory
shm_path = f"/dev/shm{SHM_NAME}"

# Check if the shared memory exists
if not os.path.exists(shm_path):
    raise FileNotFoundError(f"Shared memory {SHM_NAME} not found. Is the server running?")

with open(shm_path, 'r+b') as f:
    with mmap.mmap(f.fileno(), SHM_SIZE, access=mmap.ACCESS_READ) as shm:
        offset = 0
        # Use 'Q' for 8-byte size_t on 64-bit systems (or 'I' for 4-byte on 32-bit systems)
        key_length = struct.unpack('Q', shm[offset:offset + 8])[0]
        offset += 8
        key = shm[offset:offset + key_length].decode('utf-8')
        offset += key_length
        
        value_length = struct.unpack('Q', shm[offset:offset + 8])[0]
        offset += 8
        value = shm[offset:offset + value_length].decode('utf-8')
        print(f"Retrieved '{key}' with value '{value}' from shared memory.")
