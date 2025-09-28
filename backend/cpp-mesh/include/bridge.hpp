#pragma once

#include <string>
#include "ring_buffer.hpp"
#include "network.hpp"  // <-- integrate with MeshNode

// Utility function
std::string bridge_message(const std::string &in);

// Bridge links MeshNode (Dev A) with RingBuffer (Dev B).
class Bridge {
public:
    Bridge(MeshNode &mesh, RingBuffer &buffer, int port);
    void start_server();

private:
    MeshNode &mesh_;
    RingBuffer &buffer_;
    int port_;

    void handle_send(const std::string &body);
    std::string handle_recv(long long since_ts);
};
