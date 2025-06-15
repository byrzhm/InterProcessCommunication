CXX = g++
CXXFLAGS = -std=c++11 -Wall -Wextra -O3

all: benchmark_server

benchmark_server: benchmark_server.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< -lrt -pthread

clean:
	rm -f benchmark_server

.PHONY: all clean
