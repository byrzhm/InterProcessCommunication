CXX = g++
CXXFLAGS = -std=c++11 -Wall -Wextra -O3

all: unix_domain_socket_server unix_domain_socket_client

unix_domain_socket_server: unix_domain_socket_server.cpp
	$(CXX) $(CXXFLAGS) -o $@ $<

unix_domain_socket_client: unix_domain_socket_client.cpp
	$(CXX) $(CXXFLAGS) -o $@ $<

clean:
	rm -f unix_domain_socket_server unix_domain_socket_client *.o

.PHONY: all clean
