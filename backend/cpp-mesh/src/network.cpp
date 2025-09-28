#include "network.hpp"
#include "utils.hpp"             // Dev B utilities
#include <nlohmann/json.hpp>
#include <iostream>
#include <algorithm>
#include <chrono>

using json = nlohmann::json;

/// ------------------------- SESSION -----------------------------

Session::Session(asio::ip::tcp::socket socket, MeshNode &owner)
    : socket_(std::move(socket)), owner_(owner) {}

void Session::start() {
    do_read();   // begin reading immediately
}

void Session::do_read() {
    auto self = shared_from_this();
    asio::async_read_until(socket_, buffer_, '\n',
        [this, self](std::error_code ec, std::size_t /*bytes*/) {
            if (ec) {
                closed_ = true;
                return;
            }

            std::istream is(&buffer_);
            std::string line;
            std::getline(is, line);

            if (!line.empty()) {
                saw_activity();

                // Try parsing JSON before passing it up
                json j;
                if (devb::Utils::parse_json(line, j)) {
                    owner_.handle_line(self, line);
                } else {
                    std::cerr << "[WARN] Invalid JSON received: " << line << "\n";
                }
            }

            do_read(); // continue listening
        });
}

void Session::do_write() {
    if (write_queue_.empty() || closed_) {
        writing_ = false;
        return;
    }
    writing_ = true;

    auto self = shared_from_this();
    asio::async_write(socket_, asio::buffer(write_queue_.front()),
        [this, self](std::error_code ec, std::size_t /*bytes*/) {
            if (ec) {
                closed_ = true;
                return;
            }

            write_queue_.pop_front();
            if (!write_queue_.empty()) {
                do_write();
            } else {
                writing_ = false;
            }
        });
}

void Session::deliver(const std::string& text) {
    if (closed_) return;

    // Wrap outgoing message in standardized JSON
    json payload = { {"text", text} };
    auto msg = devb::Utils::create_message("chat", payload, owner_.node_id());
    std::string wire = devb::Utils::json_to_string(msg);

    write_queue_.push_back(wire + "\n");

    if (!writing_) {
        do_write();
    }
}

void Session::close() {
    if (closed_) return;
    closed_ = true;
    writing_ = false;
    write_queue_.clear();

    std::error_code ec;
    socket_.shutdown(asio::ip::tcp::socket::shutdown_both, ec);
    socket_.close(ec);
}

/// ------------------------- MESH NODE -----------------------------

MeshNode::MeshNode(asio::io_context& io, int listen_port, std::string node_id)
    : io_(io),
      acceptor_(io, asio::ip::tcp::endpoint(asio::ip::tcp::v4(), listen_port)),
      node_id_(std::move(node_id)),
      hb_timer_(io) {}

void MeshNode::start() {
    do_accept();
    start_heartbeat();
}

void MeshNode::do_accept() {
    acceptor_.async_accept(
        [this](std::error_code ec, asio::ip::tcp::socket socket) {
            if (!ec) {
                auto s = std::make_shared<Session>(std::move(socket), *this);
                peers_.push_back(s);
                s->start();
                std::cout << "[ACCEPT] peers=" << peers_.size() << "\n";
            }
            do_accept();
        });
}

void MeshNode::connect_to_peer(const std::string& host, int port) {
    asio::ip::tcp::resolver resolver(io_);
    auto endpoints = resolver.resolve(host, std::to_string(port));
    auto sock = std::make_shared<asio::ip::tcp::socket>(io_);

    asio::async_connect(*sock, endpoints,
        [this, sock](std::error_code ec, const asio::ip::tcp::endpoint&) {
            if (ec) {
                std::cerr << "[CONNECT] failed: " << ec.message() << "\n";
                return;
            }
            auto s = std::make_shared<Session>(std::move(*sock), *this);
            peers_.push_back(s);
            s->start();
            std::cout << "[CONNECT] ok, peers=" << peers_.size() << "\n";
        });
}

void MeshNode::broadcast(const std::string& line) {
    for (auto it = peers_.begin(); it != peers_.end();) {
        const auto& s = *it;
        if (!s->alive()) {
            it = peers_.erase(it);
            continue;
        }
        s->deliver(line);
        ++it;
    }
}

void MeshNode::handle_line(const std::shared_ptr<Session>& /*who*/, const std::string& line) {
    try {
        auto j = json::parse(line);

        if (!devb::Utils::validate_message_format(j)) {
            if (message_handler_) message_handler_(line);
            return;
        }

        WireMsg m = j.get<WireMsg>();

        // Deduplication
        if (seen_ids_.count(m.msg_id)) return;
        seen_ids_.insert(m.msg_id);

        // TTL-based rebroadcast
        if (m.ttl > 0) {
            m.ttl -= 1;
            broadcast(json(m).dump());
        }

        // Notify upper layer
        if (message_handler_) message_handler_(line);
    }
    catch (const std::exception& e) {
        std::cerr << "[PARSE ERROR] " << e.what() << "\n";
    }
}

void MeshNode::remove_session(const std::shared_ptr<Session>& s) {
    peers_.erase(std::remove(peers_.begin(), peers_.end(), s), peers_.end());
    std::cout << "[REMOVE] peers=" << peers_.size() << "\n";
}

void MeshNode::start_heartbeat() {
    hb_timer_.expires_after(std::chrono::seconds(2));
    schedule_next_heartbeat();
}

void MeshNode::schedule_next_heartbeat() {
    hb_timer_.async_wait([this](std::error_code ec) {
        if (ec) return;

        WireMsg ping;
        ping.msg_id = node_id_ + "-ping-" +
            std::to_string(std::chrono::steady_clock::now().time_since_epoch().count());
        ping.type = "ping";
        ping.sender = node_id_;
        ping.priority = 0;
        ping.timestamp = (long long)std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
        ping.ttl = 0;
        ping.content = "";

        broadcast(json(ping).dump());

        peers_.erase(std::remove_if(peers_.begin(), peers_.end(),
            [](const std::shared_ptr<Session>& s) { return !s->alive(); }), peers_.end());

        hb_timer_.expires_after(std::chrono::seconds(2));
        schedule_next_heartbeat();
    });
}
