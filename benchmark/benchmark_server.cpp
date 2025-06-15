#include <chrono>
#include <cstring>
#include <fcntl.h>
#include <iostream>
#include <string>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <vector>

// Constants for shared memory
constexpr const char *SHM_NAME = "/benchmark_shared_memory";
constexpr size_t SHM_SIZE = 10 * 1024 * 1024; // 10MB

// Constants for unix domain socket
constexpr const char *SOCKET_PATH = "/tmp/benchmark_unix_socket";

// Function to setup shared memory
int setup_shared_memory(const std::vector<uint8_t>& data) {
    // Create shared memory
    int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    if (shm_fd < 0) {
        std::cerr << "Error creating shared memory" << std::endl;
        return -1;
    }

    // Set the size of the shared memory segment
    if (ftruncate(shm_fd, SHM_SIZE) == -1) {
        std::cerr << "Error setting shared memory size" << std::endl;
        close(shm_fd);
        shm_unlink(SHM_NAME);
        return -1;
    }

    // Map the shared memory segment
    void *shm_ptr = mmap(nullptr, SHM_SIZE, PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (shm_ptr == MAP_FAILED) {
        std::cerr << "Error mapping shared memory" << std::endl;
        close(shm_fd);
        shm_unlink(SHM_NAME);
        return -1;
    }

    // Copy data size to shared memory
    size_t data_size = data.size();
    memcpy(shm_ptr, &data_size, sizeof(data_size));
    
    // Copy data to shared memory
    memcpy(static_cast<char*>(shm_ptr) + sizeof(data_size), data.data(), data_size);

    // Unmap the shared memory
    munmap(shm_ptr, SHM_SIZE);

    return shm_fd;
}

// Function to setup unix domain socket
int setup_unix_socket() {
    // Create socket
    int server_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (server_fd < 0) {
        std::cerr << "Error creating socket" << std::endl;
        return -1;
    }

    // Define address
    struct sockaddr_un server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sun_family = AF_UNIX;
    strncpy(server_addr.sun_path, SOCKET_PATH, sizeof(server_addr.sun_path) - 1);

    // Remove any existing socket file
    unlink(SOCKET_PATH);

    // Bind socket
    if (bind(server_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        std::cerr << "Error binding socket" << std::endl;
        close(server_fd);
        return -1;
    }

    // Listen for connections
    if (listen(server_fd, 5) < 0) {
        std::cerr << "Error listening on socket" << std::endl;
        close(server_fd);
        unlink(SOCKET_PATH);
        return -1;
    }

    return server_fd;
}

// Function to send data over unix socket
bool send_data_over_socket(int client_fd, const std::vector<uint8_t>& data) {
    // Send data size
    size_t data_size = data.size();
    if (send(client_fd, &data_size, sizeof(data_size), 0) < 0) {
        std::cerr << "Error sending data size" << std::endl;
        return false;
    }

    // Send data
    size_t total_sent = 0;
    while (total_sent < data_size) {
        ssize_t sent = send(client_fd, data.data() + total_sent, data_size - total_sent, 0);
        if (sent < 0) {
            std::cerr << "Error sending data" << std::endl;
            return false;
        }
        total_sent += sent;
    }

    return true;
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <mode> <size_in_kb>" << std::endl;
        std::cerr << "  mode: 'shm' for shared memory or 'socket' for unix domain socket" << std::endl;
        std::cerr << "  size_in_kb: size of data to transfer in KB" << std::endl;
        return 1;
    }

    std::string mode = argv[1];
    size_t data_size_kb = std::stoul(argv[2]);
    size_t data_size_bytes = data_size_kb * 1024;

    // Create random data
    std::vector<uint8_t> data(data_size_bytes);
    for (size_t i = 0; i < data_size_bytes; ++i) {
        data[i] = static_cast<uint8_t>(rand() % 256);
    }

    if (mode == "shm") {
        // Benchmark shared memory
        auto start_time = std::chrono::high_resolution_clock::now();
        
        int shm_fd = setup_shared_memory(data);
        if (shm_fd < 0) {
            return 1;
        }

        // Wait for client to connect and read (indicated by a signal or other mechanism)
        std::cout << "Shared memory set up. Size: " << data_size_kb << " KB" << std::endl;
        std::cout << "Waiting for client to read data..." << std::endl;
        
        // Block until input to simulate waiting for client
        std::cout << "Press Enter when client has read data..." << std::endl;
        std::cin.get();
        
        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
        
        std::cout << "Shared memory transfer completed in " << duration.count() << " ms" << std::endl;
        
        // Clean up
        close(shm_fd);
        shm_unlink(SHM_NAME);
    }
    else if (mode == "socket") {
        // Benchmark unix domain socket
        int server_fd = setup_unix_socket();
        if (server_fd < 0) {
            return 1;
        }

        std::cout << "Unix domain socket set up. Size: " << data_size_kb << " KB" << std::endl;
        std::cout << "Waiting for client connection..." << std::endl;

        // Accept connection
        struct sockaddr_un client_addr;
        socklen_t client_len = sizeof(client_addr);
        int client_fd = accept(server_fd, (struct sockaddr*)&client_addr, &client_len);
        if (client_fd < 0) {
            std::cerr << "Error accepting connection" << std::endl;
            close(server_fd);
            unlink(SOCKET_PATH);
            return 1;
        }

        std::cout << "Client connected. Sending data..." << std::endl;

        auto start_time = std::chrono::high_resolution_clock::now();
        
        if (!send_data_over_socket(client_fd, data)) {
            close(client_fd);
            close(server_fd);
            unlink(SOCKET_PATH);
            return 1;
        }

        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
        
        std::cout << "Unix domain socket transfer completed in " << duration.count() << " ms" << std::endl;
        
        // Clean up
        close(client_fd);
        close(server_fd);
        unlink(SOCKET_PATH);
    }
    else {
        std::cerr << "Unknown mode: " << mode << std::endl;
        return 1;
    }

    return 0;
}
