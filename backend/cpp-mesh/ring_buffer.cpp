#include "ring_buffer.hpp"
#include <mutex>

RingBuffer::RingBuffer(size_t capacity)
    : capacity_(capacity), buf_(capacity) {}

void RingBuffer::push(long long timestamp, const std::string &json_text) {
    std::lock_guard<std::mutex> lock(mtx_);
    buf_[head_] = {timestamp, json_text};

    if (count_ < capacity_) {
        ++count_;
    }

    head_ = (head_ + 1) % capacity_;
}

std::vector<StoredMessage> RingBuffer::get_since(long long since_ts) {
    std::lock_guard<std::mutex> lock(mtx_);
    std::vector<StoredMessage> result;

    for (size_t i = 0; i < count_; ++i) {
        size_t index = (head_ + capacity_ - count_ + i) % capacity_;
        if (buf_[index].timestamp > since_ts) {
            result.push_back(buf_[index]);
        }
    }

    return result;
}

bool RingBuffer::empty() const {
    std::lock_guard<std::mutex> lock(mtx_);
    return count_ == 0;
}

size_t RingBuffer::size() const {
    std::lock_guard<std::mutex> lock(mtx_);
    return count_;
}

void RingBuffer::clear() {
    std::lock_guard<std::mutex> lock(mtx_);
    count_ = 0;
    head_ = 0;
}
