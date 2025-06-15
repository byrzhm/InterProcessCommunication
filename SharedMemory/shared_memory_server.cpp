#include <cstring>
#include <fcntl.h>
#include <iostream>
#include <sys/mman.h>
#include <unistd.h>
#include <thread>

constexpr const char *SHM_NAME = "/my_shared_memory";
constexpr size_t SHM_SIZE = 1024 * 1024;

int main() {
  // Create SHM
  int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
  ftruncate(shm_fd, SHM_SIZE);
  void *shm_ptr = mmap(nullptr, SHM_SIZE, PROT_WRITE, MAP_SHARED, shm_fd, 0);

  // Store object
  const char *key = "name";
  const char *value = "John Doe";
  size_t offset = 0;
  size_t key_len = strlen(key);
  size_t value_len = strlen(value);

  memcpy(static_cast<char *>(shm_ptr) + offset, &key_len, sizeof(key_len));
  offset += sizeof(key_len);
  memcpy(static_cast<char *>(shm_ptr) + offset, key, key_len);
  offset += key_len;

  memcpy(static_cast<char *>(shm_ptr) + offset, &value_len, sizeof(value_len));
  offset += sizeof(value_len);
  memcpy(static_cast<char *>(shm_ptr) + offset + sizeof(value_len), value, value_len);
  offset += value_len;

  std::cout << "Stored '" << key << "' with value '" << value << "' in shared memory." << std::endl;

  std::this_thread::sleep_for(std::chrono::seconds(10));

  close(shm_fd);
  shm_unlink(SHM_NAME);
  std::cout << "Shared memory cleaned up." << std::endl;
  return 0;
}