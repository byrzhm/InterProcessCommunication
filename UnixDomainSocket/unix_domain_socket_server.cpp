#include <cstring>
#include <iostream>
#include <string>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

constexpr const char *SOCKET_PATH = "/tmp/unix_domain_socket_example";

int main() {
    // Create socket
    int server_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (server_fd < 0) {
        std::cerr << "Error creating socket" << std::endl;
        return 1;
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
        return 1;
    }

    // Listen for connections
    if (listen(server_fd, 5) < 0) {
        std::cerr << "Error listening on socket" << std::endl;
        close(server_fd);
        unlink(SOCKET_PATH);
        return 1;
    }

    std::cout << "Server is listening on " << SOCKET_PATH << std::endl;

    // Store the data we want to send
    const std::string key = "name";
    const std::string value = "John Doe";

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

    // Send key-value pair
    // Format: [key_length][key][value_length][value]
    size_t key_len = key.length();
    size_t value_len = value.length();

    // Send key length
    if (send(client_fd, &key_len, sizeof(key_len), 0) < 0) {
        std::cerr << "Error sending key length" << std::endl;
    }

    // Send key
    if (send(client_fd, key.c_str(), key_len, 0) < 0) {
        std::cerr << "Error sending key" << std::endl;
    }

    // Send value length
    if (send(client_fd, &value_len, sizeof(value_len), 0) < 0) {
        std::cerr << "Error sending value length" << std::endl;
    }

    // Send value
    if (send(client_fd, value.c_str(), value_len, 0) < 0) {
        std::cerr << "Error sending value" << std::endl;
    }

    std::cout << "Stored '" << key << "' with value '" << value << "' and sent to client." << std::endl;

    // Clean up
    close(client_fd);
    close(server_fd);
    unlink(SOCKET_PATH);
    
    std::cout << "Socket cleaned up." << std::endl;
    return 0;
}
