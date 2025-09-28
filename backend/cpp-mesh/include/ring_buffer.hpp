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
