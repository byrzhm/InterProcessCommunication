CXX      := g++
CXXFLAGS := -std=c++11 -Wall -Wextra -O3
LDFLAGS  := -lrt

all: shared_memory_server shared_memory_client

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

shared_memory_server: shared_memory_server.o
	$(CXX) $< -o $@ $(LDFLAGS)

shared_memory_client: shared_memory_client.o
	$(CXX) $< -o $@ $(LDFLAGS)

clean:
	rm -f *.o shared_memory_server shared_memory_client

.PHONY: all clean