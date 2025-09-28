/*
MeshNode → the whole network node (your computer in the mesh).
- Starts listening for connections.
- Keeps track of all peers (friends).
- Decides what to do with messages (rebroadcast, drop, or pass to Dev B).

Session → one connection to another peer.
- Reads lines (messages) from that peer.
- Sends lines (messages) to that peer.
*/

#pragma once
#define ASIO_STANDALONE
#include <asio.hpp>
#include <memory>
#include <functional>
#include <string>
#include <vector>
#include <unordered_set>
#include <deque>
#include "message.hpp"

class Session;

// ===================== MESH NODE =====================
class MeshNode {
public:
    // Type alias for the callback Dev B sets to handle new messages.
    using MsgHandler = std::function<void(const std::string&)>;

    // Create a mesh node with:
    // - io: the ASIO event loop
    // - listen_port: the TCP port this node listens on
    // - node_id: unique ID/name of this node
    MeshNode(asio::io_context& io, int listen_port, std::string node_id);

    // Start listening for new connections and schedule heartbeats
    void start();

    // Connect to another peer given host:port
    void connect_to_peer(const std::string& host, int port);

    // Broadcast a line (string message) to all connected peers
    void broadcast(const std::string& line);

    // Dev B uses this to set the callback for incoming messages
    void on_message(MsgHandler handler) { message_handler_ = std::move(handler); }

    // Return this node’s ID
    const std::string& node_id() const { return node_id_; }

    // Handle a line received from one peer:
    // - parse JSON
    // - deduplicate
    // - decrement TTL
    // - rebroadcast if needed
    // - pass to Dev B (message_handler_)
    void handle_line(const std::shared_ptr<Session>& who, const std::string& line);

private:
    // Accept incoming TCP connections
    void do_accept();

    // Remove a session from the peer list (when disconnected)
    void remove_session(const std::shared_ptr<Session>& s);

    // Start sending periodic heartbeat pings
    void start_heartbeat();

    // Schedule the next heartbeat (called repeatedly)
    void schedule_next_heartbeat();

private:
    asio::io_context& io_;                 // ASIO event loop
    asio::ip::tcp::acceptor acceptor_;     // TCP acceptor for new connections
    std::string node_id_;                  // unique node ID

    std::vector<std::shared_ptr<Session>> peers_;   // list of connected peers
    std::unordered_set<std::string> seen_ids_;      // IDs of messages already seen

    MsgHandler message_handler_;           // callback for new messages
    asio::steady_timer hb_timer_{io_};     // timer for heartbeat events
};

// ===================== SESSION =====================
// Represents a single connection to one peer
class Session : public std::enable_shared_from_this<Session> {
public:
    // Construct with a socket + reference to owner MeshNode
    Session(asio::ip::tcp::socket socket, MeshNode& owner);

    // Start async reading from this peer
    void start();

    // Send a line (message) to this peer
    void deliver(const std::string& line);

    // Reset missed heartbeat count (peer is alive)
    void saw_activity() { missed_heartbeats_ = 0; }

    // Check if the connection is alive
    bool alive() const { return !closed_; }

    // Close the socket
    void close();

private:
    // Read loop (async until "\n")
    void do_read();

    // Write loop (send queued messages)
    void do_write();

private:
    asio::ip::tcp::socket socket_;         // TCP socket for this connection
    MeshNode& owner_;                      // back reference to owning MeshNode
    asio::streambuf buffer_;               // buffer for incoming data

    std::deque<std::string> write_queue_;  // queue of outgoing messages
    bool writing_{false};                  // true if a write is in progress

    int missed_heartbeats_{0};             // counter of missed heartbeats
    bool closed_{false};                   // whether session is closed
};
