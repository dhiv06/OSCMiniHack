#pragma once

#include <vector>
#include <string>
#include <mutex>

struct StoredMessage {
    long long timestamp;
    std::string json_text;
};

class RingBuffer {
public:
    explicit RingBuffer(size_t capacity);
    void push(long long timestamp, const std::string &json_text);
    std::vector<StoredMessage> get_since(long long since_ts);

    bool empty() const;
    size_t size() const;
    void clear();

private:
    size_t capacity_;
    std::vector<StoredMessage> buf_;
    size_t head_ = 0;
    size_t count_ = 0;
    mutable std::mutex mtx_;
};
bridge.hpp: #pragma once

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
