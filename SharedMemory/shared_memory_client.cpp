#include <cstring>
#include <fcntl.h>
#include <iostream>
#include <sys/mman.h>
#include <unistd.h>

constexpr const char *SHM_NAME = "/my_shared_memory";
constexpr size_t SHM_SIZE = 1024 * 1024;

int main(int argc, char *argv[]) {
  // Open SHM
  int shm_fd = shm_open(SHM_NAME, O_RDONLY, 0666);
  void *shm_ptr = mmap(nullptr, SHM_SIZE, PROT_READ, MAP_SHARED, shm_fd, 0);

  size_t offset = 0;
  size_t key_len;
  memcpy(&key_len, static_cast<char *>(shm_ptr) + offset, sizeof(key_len));
  offset += sizeof(key_len);
  std::string key(static_cast<char *>(shm_ptr) + offset, key_len);
  offset += key_len;

  size_t value_len;
  memcpy(&value_len, static_cast<char *>(shm_ptr) + offset, sizeof(value_len));
  offset += sizeof(value_len);
  std::string value(static_cast<char *>(shm_ptr) + offset, value_len);
  offset += value_len;

  std::cout << "Retrieved '" << key << "' with value '" << value
            << "' from shared memory." << std::endl;

  return 0;
}