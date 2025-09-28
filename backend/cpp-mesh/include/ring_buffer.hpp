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

    // Add a message (timestamp + JSON text)
    void push(long long timestamp, const std::string &json_text);

    // Get all messages with timestamp > since_ts (newer than)
    std::vector<StoredMessage> get_since(long long since_ts);

    // Helpers
    bool empty() const;
    size_t size() const;
    void clear();

private:
    size_t capacity_;
    std::vector<StoredMessage> buf_;
    size_t head_ = 0;   // next write position
    size_t count_ = 0;  // how many valid entries exist (<= capacity_)
    mutable std::mutex mtx_;
};
