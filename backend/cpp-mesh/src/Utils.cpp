#include "utils.hpp"
#include <sstream>
#include <iomanip>
#include <fstream>
#include <random>
#include <algorithm>
#include <cctype>
#include <openssl/sha.h>
#include <openssl/md5.h>
#include <iomanip>
#include <chrono>
#include <ctime>
#include <stdexcept>
#include <cstring>

namespace devb {

// ===== Time utilities =====
uint64_t Utils::current_timestamp_ms() {
    return std::chrono::duration_cast<std::chrono::milliseconds>(
               std::chrono::system_clock::now().time_since_epoch())
        .count();
}

uint64_t Utils::current_timestamp_s() {
    return std::chrono::duration_cast<std::chrono::seconds>(
               std::chrono::system_clock::now().time_since_epoch())
        .count();
}

std::string Utils::timestamp_to_string(uint64_t timestamp_ms) {
    std::time_t t = timestamp_ms / 1000;
    std::tm tm{};
#ifdef _WIN32
    localtime_s(&tm, &t);
#else
    localtime_r(&t, &tm);
#endif
    char buffer[64];
    std::strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", &tm);
    return std::string(buffer);
}

uint64_t Utils::elapsed_ms(uint64_t start_time) {
    return current_timestamp_ms() - start_time;
}

// ===== String utilities =====
std::string Utils::trim(const std::string& str) {
    size_t start = str.find_first_not_of(" \t\n\r");
    size_t end = str.find_last_not_of(" \t\n\r");
    return (start == std::string::npos) ? "" : str.substr(start, end - start + 1);
}

std::vector<std::string> Utils::split(const std::string& str, char delimiter) {
    std::vector<std::string> tokens;
    std::stringstream ss(str);
    std::string item;
    while (std::getline(ss, item, delimiter)) {
        tokens.push_back(item);
    }
    return tokens;
}

std::string Utils::join(const std::vector<std::string>& parts, const std::string& delimiter) {
    std::ostringstream oss;
    for (size_t i = 0; i < parts.size(); ++i) {
        oss << parts[i];
        if (i < parts.size() - 1) oss << delimiter;
    }
    return oss.str();
}

std::string Utils::to_upper(const std::string& str) {
    std::string result = str;
    std::transform(result.begin(), result.end(), result.begin(), ::toupper);
    return result;
}

std::string Utils::to_lower(const std::string& str) {
    std::string result = str;
    std::transform(result.begin(), result.end(), result.begin(), ::tolower);
    return result;
}

bool Utils::starts_with(const std::string& str, const std::string& prefix) {
    return str.rfind(prefix, 0) == 0;
}

bool Utils::ends_with(const std::string& str, const std::string& suffix) {
    if (suffix.size() > str.size()) return false;
    return std::equal(suffix.rbegin(), suffix.rend(), str.rbegin());
}

// ===== JSON utilities =====
bool Utils::parse_json(const std::string& json_str, nlohmann::json& result) {
    try {
        result = nlohmann::json::parse(json_str);
        return true;
    } catch (...) {
        return false;
    }
}

std::string Utils::json_to_string(const nlohmann::json& json, bool pretty) {
    try {
        return pretty ? json.dump(2) : json.dump();
    } catch (...) {
        return "";
    }
}

bool Utils::has_required_fields(const nlohmann::json& json, const std::vector<std::string>& required_fields) {
    for (const auto& f : required_fields) {
        if (!json.contains(f)) return false;
    }
    return true;
}

nlohmann::json Utils::create_message(const std::string& type, const nlohmann::json& payload, const std::string& sender_id) {
    nlohmann::json j;
    j["type"] = type;
    j["payload"] = payload;
    j["sender_id"] = sender_id;
    j["timestamp"] = current_timestamp_ms();
    return j;
}

bool Utils::extract_message_components(const nlohmann::json& message_json,
                                       std::string& type,
                                       nlohmann::json& payload,
                                       std::string& sender_id,
                                       uint64_t& timestamp) {
    if (!has_required_fields(message_json, {"type", "payload", "timestamp"})) return false;
    try {
        type = message_json.at("type").get<std::string>();
        payload = message_json.at("payload");
        sender_id = message_json.value("sender_id", "");
        timestamp = message_json.at("timestamp").get<uint64_t>();
        return true;
    } catch (...) {
        return false;
    }
}

bool Utils::validate_message_format(const nlohmann::json& message_json) {
    return has_required_fields(message_json, {"type", "payload", "timestamp"});
}

// ===== Base64 =====
const std::string Utils::base64_chars_ =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

bool Utils::is_base64(unsigned char c) {
    return (isalnum(c) || (c == '+') || (c == '/'));
}

std::string Utils::base64_encode(const std::string& input) {
    unsigned char const* bytes_to_encode = reinterpret_cast<const unsigned char*>(input.c_str());
    size_t in_len = input.size();
    std::string ret;
    int i = 0;
    unsigned char char_array_3[3], char_array_4[4];

    while (in_len--) {
        char_array_3[i++] = *(bytes_to_encode++);
        if (i == 3) {
            char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
            char_array_4[1] = ((char_array_3[0] & 0x03) << 4) +
                              ((char_array_3[1] & 0xf0) >> 4);
            char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) +
                              ((char_array_3[2] & 0xc0) >> 6);
            char_array_4[3] = char_array_3[2] & 0x3f;

            for (i = 0; i < 4; i++) ret += base64_chars_[char_array_4[i]];
            i = 0;
        }
    }

    if (i) {
        for (int j = i; j < 3; j++) char_array_3[j] = '\0';
        char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
        char_array_4[1] = ((char_array_3[0] & 0x03) << 4) +
                          ((char_array_3[1] & 0xf0) >> 4);
        char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) +
                          ((char_array_3[2] & 0xc0) >> 6);

        for (int j = 0; j < i + 1; j++) ret += base64_chars_[char_array_4[j]];
        while (i++ < 3) ret += '=';
    }

    return ret;
}

std::string Utils::base64_decode(const std::string& encoded_string) {
    int in_len = encoded_string.size();
    int i = 0, in_ = 0;
    unsigned char char_array_4[4], char_array_3[3];
    std::string ret;

    while (in_len-- && (encoded_string[in_] != '=') && is_base64(encoded_string[in_])) {
        char_array_4[i++] = encoded_string[in_]; in_++;
        if (i == 4) {
            for (i = 0; i < 4; i++) char_array_4[i] = base64_chars_.find(char_array_4[i]);
            char_array_3[0] = (char_array_4[0] << 2) +
                              ((char_array_4[1] & 0x30) >> 4);
            char_array_3[1] = ((char_array_4[1] & 0xf) << 4) +
                              ((char_array_4[2] & 0x3c) >> 2);
            char_array_3[2] = ((char_array_4[2] & 0x3) << 6) +
                              char_array_4[3];

            for (i = 0; i < 3; i++) ret += char_array_3[i];
            i = 0;
        }
    }

    if (i) {
        for (int j = i; j < 4; j++) char_array_4[j] = 0;
        for (int j = 0; j < 4; j++) char_array_4[j] = base64_chars_.find(char_array_4[j]);
        char_array_3[0] = (char_array_4[0] << 2) +
                          ((char_array_4[1] & 0x30) >> 4);
        char_array_3[1] = ((char_array_4[1] & 0xf) << 4) +
                          ((char_array_4[2] & 0x3c) >> 2);

        for (int j = 0; j < i - 1; j++) ret += char_array_3[j];
    }

    return ret;
}

// ===== URL encode/decode =====
std::string Utils::url_encode(const std::string& input) {
    std::ostringstream oss;
    for (unsigned char c : input) {
        if (isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') {
            oss << c;
        } else {
            oss << '%' << std::uppercase << std::hex << int(c);
        }
    }
    return oss.str();
}

std::string Utils::url_decode(const std::string& input) {
    std::string result;
    for (size_t i = 0; i < input.length(); i++) {
        if (input[i] == '%' && i + 2 < input.length()) {
            std::string hex = input.substr(i + 1, 2);
            char c = static_cast<char>(std::stoi(hex, nullptr, 16));
            result += c;
            i += 2;
        } else if (input[i] == '+') {
            result += ' ';
        } else {
            result += input[i];
        }
    }
    return result;
}

// ===== Hashing =====
std::string Utils::sha256(const std::string& input) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(reinterpret_cast<const unsigned char*>(input.c_str()), input.size(), hash);
    std::ostringstream oss;
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++)
        oss << std::hex << std::setw(2) << std::setfill('0') << (int)hash[i];
    return oss.str();
}

std::string Utils::md5(const std::string& input) {
    unsigned char digest[MD5_DIGEST_LENGTH];
    MD5(reinterpret_cast<const unsigned char*>(input.c_str()), input.size(), digest);
    std::ostringstream oss;
    for (int i = 0; i < MD5_DIGEST_LENGTH; i++)
        oss << std::hex << std::setw(2) << std::setfill('0') << (int)digest[i];
    return oss.str();
}

// ===== Random =====
std::string Utils::random_string(size_t length, const std::string& charset) {
    std::default_random_engine rng(std::random_device{}());
    std::uniform_int_distribution<> dist(0, charset.size() - 1);
    std::string result;
    for (size_t i = 0; i < length; ++i) result += charset[dist(rng)];
    return result;
}

// ===== File =====
std::string Utils::read_file(const std::string& filename) {
    std::ifstream ifs(filename, std::ios::binary);
    if (!ifs) return "";
    return std::string((std::istreambuf_iterator<char>(ifs)), std::istreambuf_iterator<char>());
}

bool Utils::write_file(const std::string& filename, const std::string& content) {
    std::ofstream ofs(filename, std::ios::binary);
    if (!ofs) return false;
    ofs << content;
    return true;
}

bool Utils::file_exists(const std::string& filename) {
    std::ifstream ifs(filename);
    return ifs.good();
}

} // namespace devb
