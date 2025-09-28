/// A letter template you always fill out before sending.  The other nodes know exactly what to expect when they open the letter.
#pragma once
#include <string>
#include <cstdint>
#include <nlohmann/json.hpp>
/// Basic structure for each message in the mesh network
struct WireMsg{
    std::string msg_id;
    std::string type;
    std::string sender;
    int priority{0};
    std::int64_t timestamp{0};
    int ttl{6};
    std::string content;
    int chunk_index{0};
    int chunk_total{0};

};

///Convert WireMsg to JSON
inline void to_json(nlohmann::json& j, const WireMsg& m) {
    j = nlohmann::json{
        {"msg_id", m.msg_id},
        {"type", m.type},
        {"sender", m.sender},
        {"priority", m.priority},
        {"timestamp", m.timestamp},
        {"ttl", m.ttl},
        {"content", m.content},
        {"chunk_index", m.chunk_index},
        {"chunk_total", m.chunk_total}
    };
}
// Convert JSON -> WireMsg
inline void from_json(const nlohmann::json& j, WireMsg& m) {
    j.at("msg_id").get_to(m.msg_id);
    j.at("type").get_to(m.type);
    j.at("sender").get_to(m.sender);
    j.at("priority").get_to(m.priority);
    j.at("timestamp").get_to(m.timestamp);
    j.at("ttl").get_to(m.ttl);
    j.at("content").get_to(m.content);
    if (j.contains("chunk_index")) j.at("chunk_index").get_to(m.chunk_index);
    if (j.contains("chunk_total")) j.at("chunk_total").get_to(m.chunk_total);
}