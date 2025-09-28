#include "utils.hpp"
#include <sstream>
#include <iomanip>
#include <fstream>
#include <algorithm>
#include <random>
#include <cctype>

namespace devb {

// Initialize static members
const std::string Utils::base64_chars_ = 
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789+/";

// Time utilities
uint64_t Utils::current_timestamp_ms() {
    return std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()
    ).count();
}

uint64_t Utils::current_timestamp_s() {
    return std::chrono::duration_cast<std::chrono::seconds>(
        std::chrono::system_clock::now().time_since_epoch()
    ).count();
}

std::string Utils::timestamp_to_string(uint64_t timestamp_ms) {
    auto time_point = std::chrono::system_clock::time_point(
        std::chrono::milliseconds(timestamp_ms)
    );
    auto time_t = std::chrono::system_clock::to_time_t(time_point);
    
    std::stringstream ss;
    ss << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S");
    
    // Add milliseconds
    auto ms = timestamp_ms % 1000;
    ss << "." << std::setfill('0') << std::setw(3) << ms;
    
    return ss.str();
}

uint64_t Utils::elapsed_ms(uint64_t start_time) {
    return current_timestamp_ms() - start_time;
}

// String utilities
std::string Utils::trim(const std::string& str) {
    size_t start = str.find_first_not_of(" \t\n\r\f\v");
    if (start == std::string::npos) {
        return "";
    }
    
    size_t end = str.find_last_not_of(" \t\n\r\f\v");
    return str.substr(start, end - start + 1);
}

std::vector<std::string> Utils::split(const std::string& str, char delimiter) {
    std::vector<std::string> result;
    std::stringstream ss(str);
    std::string item;
    
    while (std::getline(ss, item, delimiter)) {
        result.push_back(item);
    }
    
    return result;
}

std::string Utils::join(const std::vector<std::string>& parts, const std::string& delimiter) {
    if (parts.empty()) {
        return "";
    }
    
    std::stringstream ss;
    for (size_t i = 0; i < parts.size(); ++i) {
        if (i > 0) {
            ss << delimiter;
        }
        ss << parts[i];
    }
    
    return ss.str();
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
    return str.length() >= prefix.length() && 
           str.compare(0, prefix.length(), prefix) == 0;
}

bool Utils::ends_with(const std::string& str, const std::string& suffix) {
    return str.length() >= suffix.length() && 
           str.compare(str.length() - suffix.length(), suffix.length(), suffix) == 0;
}

// JSON utilities
bool Utils::parse_json(const std::string& json_str, nlohmann::json& result) {
    try {
        result = nlohmann::json::parse(json_str);
        return true;
    }
    catch (const nlohmann::json::parse_error&) {
        return false;
    }
}

std::string Utils::json_to_string(const nlohmann::json& json, bool pretty) {
    try {
        if (pretty) {
            return json.dump(2); // 2-space indentation
        } else {
            return json.dump();
        }
    }
    catch (const std::exception&) {
        return "";
    }
}

bool Utils::has_required_fields(const nlohmann::json& json, const std::vector<std::string>& required_fields) {
    for (const auto& field : required_fields) {
        if (!json.contains(field)) {
            return false;
        }
    }
    return true;
}

// Message utilities
nlohmann::json Utils::create_message(const std::string& type, const nlohmann::json& payload, const std::string& sender_id) {
    nlohmann::json message;
    message["type"] = type;
    message["payload"] = payload;
    message["timestamp"] = current_timestamp_ms();
    
    if (!sender_id.empty()) {
        message["sender_id"] = sender_id;
    }
    
    return message;
}

bool Utils::extract_message_components(const nlohmann::json& message_json, 
                                     std::string& type, 
                                     nlohmann::json& payload, 
                                     std::string& sender_id, 
                                     uint64_t& timestamp) {
    try {
        if (!message_json.contains("type") || !message_json.contains("payload")) {
            return false;
        }
        
        type = message_json["type"];
        payload = message_json["payload"];
        
        if (message_json.contains("sender_id")) {
            sender_id = message_json["sender_id"];
        } else {
            sender_id = "";
        }
        
        if (message_json.contains("timestamp")) {
            timestamp = message_json["timestamp"];
        } else {
            timestamp = current_timestamp_ms();
        }
        
        return true;
    }
    catch (const std::exception&) {
        return false;
    }
}

bool Utils::validate_message_format(const nlohmann::json& message_json) {
    std::vector<std::string> required_fields = {"type", "payload"};
    return has_required_fields(message_json, required_fields);
}

// Base64 utilities
bool Utils::is_base64(unsigned char c) {
    return (isalnum(c) || (c == '+') || (c == '/'));
}

std::string Utils::base64_encode(const std::string& input) {
    std::string encoded;
    int val = 0, valb = -6;
    
    for (unsigned char c : input) {
        val = (val << 8) + c;
        valb += 8;
        while (valb >= 0) {
            encoded.push_back(base64_chars_[(val >> valb) & 0x3F]);
            valb -= 6;
        }
    }
    
    if (valb > -6) {
        encoded.push_back(base64_chars_[((val << 8) >> (valb + 8)) & 0x3F]);
    }
    
    while (encoded.size() % 4) {
        encoded.push_back('=');
    }
    
    return encoded;
}

std::string Utils::base64_decode(const std::string& input) {
    std::string decoded;
    int val = 0, valb = -8;
    
    for (unsigned char c : input) {
        if (!is_base64(c)) break;
        
        val = (val << 6) + base64_chars_.find(c);
        valb += 6;
        if (valb >= 0) {
            decoded.push_back(char((val >> valb) & 0xFF));
            valb -= 8;
        }
    }
    
    return decoded;
}

// URL encoding utilities
std::string Utils::url_encode(const std::string& input) {
    std::ostringstream escaped;
    escaped.fill('0');
    escaped << std::hex;

    for (char c : input) {
        // Keep alphanumeric and other accepted characters intact
        if (isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') {
            escaped << c;
        } else {
            // Any other characters are percent-encoded
            escaped << std::uppercase;
            escaped << '%' << std::setw(2) << int((unsigned char) c);
            escaped << std::nouppercase;
        }
    }

    return escaped.str();
}

std::string Utils::url_decode(const std::string& input) {
    std::string decoded;
    
    for (size_t i = 0; i < input.length(); ++i) {
        if (input[i] == '%' && i + 2 < input.length()) {
            int hex = 0;
            std::istringstream is(input.substr(i + 1, 2));
            if (is >> std::hex >> hex) {
                decoded += static_cast<char>(hex);
                i += 2;
            } else {
                decoded += input[i];
            }
        } else if (input[i] == '+') {
            decoded += ' ';
        } else {
            decoded += input[i];
        }
    }
    
    return decoded;
}

// Hash utilities (simplified versions - for production use a proper crypto library)
std::string Utils::sha256(const std::string& input) {
    // This is a placeholder implementation
    // In a real application, use a proper cryptographic library like OpenSSL
    std::hash<std::string> hasher;
    size_t hash = hasher(input);
    
    std::stringstream ss;
    ss << std::hex << hash;
    return ss.str();
}

std::string Utils::md5(const std::string& input) {
    // This is a placeholder implementation
    // In a real application, use a proper cryptographic library like OpenSSL
    std::hash<std::string> hasher;
    size_t hash = hasher(input + "md5_salt");
    
    std::stringstream ss;
    ss << std::hex << hash;
    return ss.str();
}

std::string Utils::random_string(size_t length, const std::string& charset) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, charset.size() - 1);
    
    std::string result;
    result.reserve(length);
    
    for (size_t i = 0; i < length; ++i) {
        result += charset[dis(gen)];
    }
    
    return result;
}

// File utilities
std::string Utils::read_file(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        return "";
    }
    
    std::stringstream buffer;
    buffer << file.rdbuf();
    return buffer.str();
}

bool Utils::write_file(const std::string& filename, const std::string& content) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        return false;
    }
    
    file << content;
    return file.good();
}

bool Utils::file_exists(const std::string& filename) {
    std::ifstream file(filename);
    return file.good();
}

} // namespace devb
