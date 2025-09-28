#include "network.hpp"

#include <nlohmann/json.hpp>
#include <iostream>
#include <algorithm>
#include <chrono>

Session::Session(asio::ip::tcp::socket socket, MeshNode &owner)
    : socket_(std::move(socket)), owner_(owner) {}

void Session::start()
{
    // as soon as a session starts, begin reading lines
    do_read();
}

void Session::do_read()
{
    auto self = shared_from_this();
    asio::async_read_until(socket_, buffer_, '\n', /// basically reading from this line, putting it into buffer, and reading until we press enter
                           [this, self](std::error_code ec, std::size_t /*bytes*/)
                           {
                               if (ec)
                               {
                                   closed_ = true; // peer disconnected or error
                                   return;
                               }

                               // read the message as a file
                               std::istream is(&buffer_);
                               std::string line;
                               std::getline(is, line);

                               if (!line.empty())
                               {
                                   saw_activity();                 // we heard from this peer, restart the last time we heard from them
                                   owner_.handle_line(self, line); // let MeshNode process i/// let dev b process it
                               }

                               // keep listening for more lines
                               do_read();
                           });
}
void Session::do_write()
{
    if (write_queue_.empty() || closed_ == true)
    {
        writing_ = false;
        return;
    }
    writing_ = true;
    auto self = shared_from_this(); /// what we are looking into momentarily
    asio::async_write(socket_, asio::buffer(write_queue_.front()),
                      [this, self](std::error_code ec, std::size_t /*bytes*/)
                      {
                          if (ec)
                          {
                              closed_ = true;
                              return;
                          }

                          write_queue_.pop_front();
                          if (!write_queue_.empty())
                          {
                              do_write();
                          }
                          else
                          {
                              writing_ = false;
                          }
                      }); /// make it deliver the first message in the queue
}
// deliver(): добиваме порака од MeshNode за испраќање кон ОВОЈ peer
void Session::deliver(const std::string& line) {
    if (closed_) {                       // ако сесијата е веќе затворена → не праќаме ништо
        return;
    }

    // секоја порака ја чуваме со завршен '\n', за другата страна да може да чита до нов ред
    write_queue_.push_back(line + "\n"); // ја ставаш пораката на крај од редицата

    // ако моментално НЕ пишуваме, стартувај испраќање
    if (!writing_) {                     // ако поштарот спие → разбуди го
        do_write();                      // почни да ја празниш редицата, една по една
    }
}
/// literally just shut down the line between two people, as it has been inactive or we want to stop using it in general
void Session::close()
{
    if(closed_)
    return;
    closed_=true;
    writing_=false;
    write_queue_.clear();
    std::error_code ec;
    socket_.shutdown(asio::ip::tcp::socket::shutdown_both, ec);
    // дури и ако има грешка (на пример "веќе е затворено") → ја игнорираме

    // 5) Затвори го сокетот и ослободи го ресурсот
    socket_.close(ec);
    // пак, ја игнорираме грешката, бидејќи може да е "веќе затворен"
}


///-------------------------MESHNODE_NETWORK-------------------------------------------------
MeshNode::MeshNode(asio::io_context& io, int listen_port, std::string node_id)
    : io_(io),                                                        // референца кон event loop
      acceptor_(io, asio::ip::tcp::endpoint(asio::ip::tcp::v4(), listen_port)), // TCP „ѕвонче“ на портот
      node_id_(std::move(node_id)),                                  // нашето име/ID
      hb_timer_(io)                                                  // тајмер за heartbeat
{}

// start(): пушти прифаќање на нови врски + стартувај heartbeat
void MeshNode::start() {
    do_accept();                // почни да слушаш нови конекции (inbound)
    start_heartbeat();          // старт на периодични пингови/чистење
}

// do_accept(): чекај inbound конекции; секоја успешно прифатена ја обвиткуваш во Session
void MeshNode::do_accept() {
    acceptor_.async_accept(     // асинхроно чекај нов socket од клиент
        [this](std::error_code ec, asio::ip::tcp::socket socket) { // handler кога некој ќе се поврзе
            if (!ec) {                                             // ако е успешно
                // направи Session од прифатениот сокет
                auto s = std::make_shared<Session>(std::move(socket), *this);
                peers_.push_back(s);                               // зачувај го во листата peers_
                s->start();                                        // стартувај читање од тој peer
                std::cout << "[ACCEPT] peers=" << peers_.size() << "\n";
            }
            do_accept();           // безусловно пак чекај следна конекција (бесконечно)
        }
    );
}

// connect_to_peer(): outbound спојување кон друг јазол (host:port)
void MeshNode::connect_to_peer(const std::string& host, int port) {
    // прво: resolve (DNS/името) во адреси (endpoints)
    asio::ip::tcp::resolver resolver(io_);                      // резолвер поврзан со истиот io_context
    auto endpoints = resolver.resolve(host, std::to_string(port)); // листа можни адреси

    // користиме помошен socket што ќе го префрлиме во Session кога ќе успееме да се поврземе
    auto sock = std::make_shared<asio::ip::tcp::socket>(io_);

    // асинхроно обидување кон сите дадени endpoints додека не успее
    asio::async_connect(*sock, endpoints,
        [this, sock](std::error_code ec, const asio::ip::tcp::endpoint& /*ep*/) {
            if (ec) {                                               // ако не успее
                std::cerr << "[CONNECT] failed: " << ec.message() << "\n";
                return;
            }
            // успех: правиме Session од поврзаниот socket
            auto s = std::make_shared<Session>(std::move(*sock), *this);
            peers_.push_back(s);                                    // зачувај го peer-от
            s->start();                                             // почни да читаш од него
            std::cout << "[CONNECT] ok, peers=" << peers_.size() << "\n";
        }
    );
}

// broadcast(): испрати ја пораката до СИТЕ активни peers (и успат исчисти мртви врски)
void MeshNode::broadcast(const std::string& line) {
    for (auto it = peers_.begin(); it != peers_.end(); ) {      // итерираме рачно за да можеме erase во место
        const auto& s = *it;                                    // тековниот Session
        if (!s->alive()) {                                      // ако е веќе затворен
            it = peers_.erase(it);                              // бриши од листата и НЕ зголемувај it
            continue;                                           // скокни на следниот без ++it
        }
        s->deliver(line);                                       // иначе: испрати ја пораката на тој peer
        ++it;                                                   // следен peer
    }
}

// handle_line(): срж на „мрежната логика“ — parse → dedupe → TTL → rebroadcast → извести Dev B
void MeshNode::handle_line(const std::shared_ptr<Session>& /*who*/, const std::string& line) {
    try {
        // 1) PARSE: пробај да ја парсираш линијата како JSON
        auto j = nlohmann::json::parse(line);

        // ако не содржи "msg_id", не е наш стандардизиран WireMsg → можеш да го проследиш како raw
        if (!j.contains("msg_id")) {
            if (message_handler_) message_handler_(line);       // Dev B ќе знае што да прави
            return;
        }

        // претвори JSON → WireMsg (благодарение на твојот to_json/from_json во message.hpp)
        WireMsg m = j.get<WireMsg>();

        // 2) DEDUPE: ако веќе сме ја виделе оваа порака → стоп (спречува бесконечни кругови)
        if (seen_ids_.find(m.msg_id) != seen_ids_.end()) {
            return;                                             // дупликат → игнорирај
        }
        seen_ids_.insert(m.msg_id);                             // означи дека сега ја видовме

        // 3) TTL: ограничи колку далеку шета пораката низ мрежата
        if (m.ttl > 0) {                                        // ако уште има „животи“
            m.ttl -= 1;                                         // потроши еден хоп
            auto fwd = nlohmann::json(m).dump();                // ре-серијализирај со нов TTL
            broadcast(fwd);                                     // препрати на сите peers
        }

        // 4) NOTIFY: кажи на Dev B (или UI) дека стигна НОВА порака (истиот оригинален string)
        if (message_handler_) message_handler_(line);
    }
    catch (const std::exception& e) {                           // ако JSON парсирањето фрли исклучок
        std::cerr << "[PARSE] " << e.what() << "\n";            // логирај предупредување
        // (по избор) можеш и raw line да ја проследиш нагоре:
        // if (message_handler_) message_handler_(line);
    }
}

// remove_session(): помошна — бриши конкретен Session од peers_ (ако сакаш експлицитно да чистиш)
void MeshNode::remove_session(const std::shared_ptr<Session>& s) {
    peers_.erase(std::remove(peers_.begin(), peers_.end(), s), peers_.end()); // remove-erase идиом
    std::cout << "[REMOVE] peers=" << peers_.size() << "\n";
}

// start_heartbeat(): иницирај прво „чукање“ по 2 секунди
void MeshNode::start_heartbeat() {
    hb_timer_.expires_after(std::chrono::seconds(2));           // кога да тргне првиот аларм
    schedule_next_heartbeat();                                  // закажи handler
}

// schedule_next_heartbeat(): handler за тајмерот кој:
// - праќа „ping“ (ttl=0 за да НЕ се препраќа)
// - чисти затворени сесии
// - се закажува пак (периодично)
void MeshNode::schedule_next_heartbeat() {
    hb_timer_.async_wait([this](std::error_code ec) {           // ќе се повика кога тајмерот ќе „свирне“
        if (ec) return;                                         // ако тајмерот е откажан → излези

        // состави минимална ping порака (ttl=0 значи: не се ребродкасти)
        WireMsg ping;
        ping.msg_id = node_id_ + "-ping-" +
            std::to_string(std::chrono::steady_clock::now().time_since_epoch().count()); // уникатен id
        ping.type = "ping";
        ping.sender = node_id_;
        ping.priority = 0;
        ping.timestamp = (long long)std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
        ping.ttl = 0;                                           // важно: да не се шири понатаму
        ping.content = "";                                      // нема корисна содржина

        broadcast(nlohmann::json(ping).dump());                 // испрати ping до сите peers

        // едноставно чистење: бриши сите што не се „alive()“
        peers_.erase(std::remove_if(peers_.begin(), peers_.end(),
            [](const std::shared_ptr<Session>& s){ return !s->alive(); }), peers_.end());

        // закажи повторно по 2 секунди (периодика)
        hb_timer_.expires_after(std::chrono::seconds(2));
        schedule_next_heartbeat();
    });
}