#include <asio.hpp>       // 🔌 networking/event loop library
#include "network.hpp"    // 🧩 our MeshNode + Session classes
#include <iostream>       // 💬 for printing to console

int main() {
    // 1) Create the io_context
    // Think of this as the "event loop brain".
    // All asynchronous (non-blocking) tasks are run inside this object.
    asio::io_context io;

    // 2) Pick a port for this node to listen on
    // Each node needs its own port (like a "door number" for messages).
    int port = 5000;

    // 3) Create a MeshNode
    // Arguments:
    //   io    -> event loop we just made
    //   port  -> the port to listen on
    //   "NodeA" -> a simple ID for this node
    MeshNode node(io, port, "NodeA");

    // 4) Attach a message handler
    // Whenever this node receives a message from a peer,
    // the handler function below will be called.
    // Right now, we just print the message to the console.
    node.on_message([](const std::string& msg) {
        std::cout << "[Got message] " << msg << std::endl;
    });

    // 5) Start listening for new connections
    // This opens the port and prepares to accept peers.
    node.start();

    // 6) Optionally connect to another peer
    // If you run another instance on port 5001,
    // uncomment this to connect NodeA (5000) to NodeB (5001).
    // node.connect_to_peer("127.0.0.1", 5001);

    // 7) Send a test broadcast
    // This will deliver the message to ALL connected peers.
    // If there are no peers yet, it won't go anywhere.
    node.broadcast("Hello from NodeA!");

    // 8) Run the event loop
    // This call blocks and keeps the program alive.
    // Behind the scenes, io.run() will:
    //   - accept new peers
    //   - read incoming messages
    //   - write outgoing messages
    //   - handle heartbeats
    io.run();

    return 0;
}
