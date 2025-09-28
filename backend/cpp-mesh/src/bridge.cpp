#include "bridge.hpp"
#include "utils.hpp"
#include <nlohmann/json.hpp>
#include <chrono>

using json = nlohmann::json;

std::string bridge_message(const std::string &in) {
    return "[bridge] " + in;
}

Bridge::Bridge(MeshNode &mesh, RingBuffer &buffer, int port)
    : mesh_(mesh), buffer_(buffer), port_(port) {}

// Parse JSON, attach timestamp, push to buffer
void Bridge::handle_send(const std::string &body) {
    try {
        auto j = json::parse(body);
        long long ts = static_cast<long long>(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()
            ).count()
        );
        j["timestamp"] = ts;
        buffer_.push(ts, j.dump());

        // also broadcast to mesh
        mesh_.broadcast(j.dump());

    } catch (const std::exception &) {
        // ignore parse errors
    }
}

// Collect messages since given timestamp
std::string Bridge::handle_recv(long long since_ts) {
    auto msgs = buffer_.get_since(since_ts);
    json arr = json::array();
    for (const auto &m : msgs) {
        try {
            arr.push_back(json::parse(m.json_text));
        } catch (...) {
            arr.push_back(m.json_text);
        }
    }
    return arr.dump();
}

void Bridge::start_server() {
    // Placeholder – connect to HTTP server if needed
}
