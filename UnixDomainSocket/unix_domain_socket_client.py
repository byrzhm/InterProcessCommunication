import socket
import struct

# Socket path
SOCKET_PATH = "/tmp/unix_domain_socket_example"

# Create a Unix domain socket
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

try:
    # Connect to the server
    client.connect(SOCKET_PATH)
    print("Connected to server")

    # Receive data
    # Format: [key_length][key][value_length][value]
    
    # Receive key length (size_t is 8 bytes on 64-bit systems)
    key_length_bytes = client.recv(8)
    key_length = struct.unpack('Q', key_length_bytes)[0]
    
    # Receive key
    key = client.recv(key_length).decode('utf-8')
    
    # Receive value length
    value_length_bytes = client.recv(8)
    value_length = struct.unpack('Q', value_length_bytes)[0]
    
    # Receive value
    value = client.recv(value_length).decode('utf-8')
    
    print(f"Retrieved '{key}' with value '{value}' from Unix domain socket.")
    
except ConnectionRefusedError:
    print("Connection refused. Make sure the server is running.")
    
except FileNotFoundError:
    print(f"Socket file {SOCKET_PATH} not found. Make sure the server is running.")
    
finally:
    client.close()
