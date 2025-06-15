#include <cstring>
#include <iostream>
#include <string>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

constexpr const char *SOCKET_PATH = "/tmp/unix_domain_socket_example";

int main() {
    // Create socket
    int client_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (client_fd < 0) {
        std::cerr << "Error creating socket" << std::endl;
        return 1;
    }

    // Define server address
    struct sockaddr_un server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sun_family = AF_UNIX;
    strncpy(server_addr.sun_path, SOCKET_PATH, sizeof(server_addr.sun_path) - 1);

    // Connect to server
    if (connect(client_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        std::cerr << "Error connecting to server. Is the server running?" << std::endl;
        close(client_fd);
        return 1;
    }

    // Receive key-value pair
    // Format: [key_length][key][value_length][value]
    
    // Receive key length
    size_t key_len;
    if (recv(client_fd, &key_len, sizeof(key_len), 0) < 0) {
        std::cerr << "Error receiving key length" << std::endl;
        close(client_fd);
        return 1;
    }

    // Receive key
    std::string key(key_len, '\0');
    if (recv(client_fd, &key[0], key_len, 0) < 0) {
        std::cerr << "Error receiving key" << std::endl;
        close(client_fd);
        return 1;
    }

    // Receive value length
    size_t value_len;
    if (recv(client_fd, &value_len, sizeof(value_len), 0) < 0) {
        std::cerr << "Error receiving value length" << std::endl;
        close(client_fd);
        return 1;
    }

    // Receive value
    std::string value(value_len, '\0');
    if (recv(client_fd, &value[0], value_len, 0) < 0) {
        std::cerr << "Error receiving value" << std::endl;
        close(client_fd);
        return 1;
    }

    std::cout << "Retrieved '" << key << "' with value '" << value << "' from Unix domain socket." << std::endl;

    // Clean up
    close(client_fd);
    
    return 0;
}
