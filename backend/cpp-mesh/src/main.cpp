#include <asio.hpp>       // 🔌 Networking/event loop library
#include "network.hpp"    // 🧩 MeshNode + Session
#include "utils.hpp"      // 🛠️ Dev B utilities
#include <iostream>       // 💬 Printing to console
#include <thread>         // 🧵 For running input loop separately
#include <atomic>         // ⚡ For clean shutdown flag

int main(int argc, char* argv[]) {
    try {
        // 1) Create the io_context (event loop brain)
        asio::io_context io;

        // 2) Determine port and node ID from args (defaults for convenience)
        int port = 5000;
        std::string node_id = "NodeA";
        if (argc > 1) port = std::stoi(argv[1]);
        if (argc > 2) node_id = argv[2];

        std::cout << "[INFO] Starting " << node_id << " on port " << port << "\n";

        // 3) Create a MeshNode
        MeshNode node(io, port, node_id);

        // 4) Attach message handler (called whenever a peer sends us something)
        node.on_message([&](const std::string& msg) {
            std::cout << "\n📩 [Message Received] " << msg << std::endl;
            std::cout << "💬 Type a message: " << std::flush;
        });

        // 5) Start listening for peers
        node.start();

        // 6) Optionally connect to a peer if specified
        if (argc > 4) {
            std::string peer_host = argv[3];
            int peer_port = std::stoi(argv[4]);
            node.connect_to_peer(peer_host, peer_port);
            std::cout << "[INFO] Trying to connect to peer at "
                      << peer_host << ":" << peer_port << "\n";
        }

        // 7) Run the io_context in a separate thread so it handles networking
        std::thread net_thread([&]() { io.run(); });

        // 8) Start chat input loop
        std::atomic<bool> running(true);
        std::string text;
        std::cout << "💬 Type a message (or /quit to exit): " << std::flush;

        while (running && std::getline(std::cin, text)) {
            if (text == "/quit") {
                running = false;
                io.stop(); // stop networking loop
                break;
            }

            // Package message as JSON
            nlohmann::json payload = { {"text", text} };
            auto msg = devb::Utils::create_message("chat", payload, node_id);

            // Send it to all peers
            node.broadcast(msg.dump());

            std::cout << "✅ Sent: " << text << std::endl;
            std::cout << "💬 Type a message: " << std::flush;
        }

        // 9) Cleanup
        if (net_thread.joinable()) net_thread.join();

    } catch (const std::exception& e) {
        std::cerr << "[ERROR] " << e.what() << "\n";
        return 1;
    }

    return 0;
}
