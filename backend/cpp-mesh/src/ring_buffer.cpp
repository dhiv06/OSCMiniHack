#include "ring_buffer.hpp"
#include <mutex>

RingBuffer::RingBuffer(size_t capacity)
    : capacity_(capacity), buf_(capacity) {}

void RingBuffer::push(long long timestamp, const std::string &json_text) {
    std::lock_guard<std::mutex> lock(mtx_);
    // write into current head_
    buf_[head_] = {timestamp, json_text};

    // grow count_ up to capacity_
    if (count_ < capacity_) {
        ++count_;
    }

    // advance head_ (circular)
    head_ = (head_ + 1) % capacity_;
}

std::vector<StoredMessage> RingBuffer::get_since(long long since_ts) {
    std::lock_guard<std::mutex> lock(mtx_);
    std::vector<StoredMessage> result;
    result.reserve(count_);

    // walk from the oldest to newest:
    // oldest index = (head_ + capacity_ - count_) % capacity_
    size_t start = (head_ + capacity_ - count_) % capacity_;
    for (size_t i = 0; i < count_; ++i) {
        size_t idx = (start + i) % capacity_;
        const auto &msg = buf_[idx];
        if (msg.timestamp > since_ts) {
            result.push_back(msg);
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
