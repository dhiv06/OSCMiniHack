#pragma once

#include <string>
#include <vector>
#include <chrono>
#include <nlohmann/json.hpp>

namespace devb {

/**
 * Utility functions for Dev B's application layer
 * Provides common functionality for message processing, JSON handling,
 * time operations, and string manipulation
 */
class Utils {
public:
    // Time utilities
    /**
     * Get current timestamp in milliseconds since epoch
     * @return Timestamp in milliseconds
     */
    static uint64_t current_timestamp_ms();

    /**
     * Get current timestamp in seconds since epoch
     * @return Timestamp in seconds
     */
    static uint64_t current_timestamp_s();

    /**
     * Convert timestamp to human readable string
     * @param timestamp_ms Timestamp in milliseconds
     * @return Human readable time string
     */
    static std::string timestamp_to_string(uint64_t timestamp_ms);

    /**
     * Get elapsed time in milliseconds
     * @param start_time Start timestamp in milliseconds
     * @return Elapsed milliseconds
     */
    static uint64_t elapsed_ms(uint64_t start_time);

    // String utilities
    /**
     * Trim whitespace from both ends of string
     * @param str String to trim
     * @return Trimmed string
     */
    static std::string trim(const std::string& str);

    /**
     * Split string by delimiter
     * @param str String to split
     * @param delimiter Delimiter character
     * @return Vector of split strings
     */
    static std::vector<std::string> split(const std::string& str, char delimiter);

    /**
     * Join vector of strings with delimiter
     * @param parts Vector of strings to join
     * @param delimiter Delimiter string
     * @return Joined string
     */
    static std::string join(const std::vector<std::string>& parts, const std::string& delimiter);

    /**
     * Convert string to uppercase
     * @param str Input string
     * @return Uppercase string
     */
    static std::string to_upper(const std::string& str);

    /**
     * Convert string to lowercase
     * @param str Input string
     * @return Lowercase string
     */
    static std::string to_lower(const std::string& str);

    /**
     * Check if string starts with prefix
     * @param str String to check
     * @param prefix Prefix to look for
     * @return true if string starts with prefix
     */
    static bool starts_with(const std::string& str, const std::string& prefix);

    /**
     * Check if string ends with suffix
     * @param str String to check
     * @param suffix Suffix to look for
     * @return true if string ends with suffix
     */
    static bool ends_with(const std::string& str, const std::string& suffix);

    // JSON utilities
    /**
     * Parse JSON string safely
     * @param json_str JSON string to parse
     * @param result Output parameter for parsed JSON
     * @return true if parsing successful
     */
    static bool parse_json(const std::string& json_str, nlohmann::json& result);

    /**
     * Convert JSON to string safely
     * @param json JSON object to stringify
     * @param pretty Whether to format with indentation
     * @return JSON string, empty if error
     */
    static std::string json_to_string(const nlohmann::json& json, bool pretty = false);

    /**
     * Check if JSON has required fields
     * @param json JSON object to check
     * @param required_fields Vector of required field names
     * @return true if all fields present
     */
    static bool has_required_fields(const nlohmann::json& json, const std::vector<std::string>& required_fields);

    // Message utilities
    /**
     * Create a standard message JSON structure
     * @param type Message type
     * @param payload Message payload
     * @param sender_id Sender identifier
     * @return JSON message object
     */
    static nlohmann::json create_message(const std::string& type, const nlohmann::json& payload, const std::string& sender_id = "");

    /**
     * Extract message components from JSON
     * @param message_json JSON message object
     * @param type Output parameter for message type
     * @param payload Output parameter for payload
     * @param sender_id Output parameter for sender ID
     * @param timestamp Output parameter for timestamp
     * @return true if extraction successful
     */
    static bool extract_message_components(const nlohmann::json& message_json, 
                                         std::string& type, 
                                         nlohmann::json& payload, 
                                         std::string& sender_id, 
                                         uint64_t& timestamp);

    /**
     * Validate message format
     * @param message_json JSON message to validate
     * @return true if message has valid format
     */
    static bool validate_message_format(const nlohmann::json& message_json);

    // Encoding/Decoding utilities
    /**
     * Base64 encode string
     * @param input Input string to encode
     * @return Base64 encoded string
     */
    static std::string base64_encode(const std::string& input);

    /**
     * Base64 decode string
     * @param input Base64 encoded string
     * @return Decoded string, empty if error
     */
    static std::string base64_decode(const std::string& input);

    /**
     * URL encode string
     * @param input Input string to encode
     * @return URL encoded string
     */
    static std::string url_encode(const std::string& input);

    /**
     * URL decode string
     * @param input URL encoded string
     * @return Decoded string
     */
    static std::string url_decode(const std::string& input);

    // Hash utilities
    /**
     * Calculate SHA256 hash of string
     * @param input Input string
     * @return Hex string of hash
     */
    static std::string sha256(const std::string& input);

    /**
     * Calculate MD5 hash of string
     * @param input Input string
     * @return Hex string of hash
     */
    static std::string md5(const std::string& input);

    /**
     * Generate random string
     * @param length Length of random string
     * @param charset Character set to use (default: alphanumeric)
     * @return Random string
     */
    static std::string random_string(size_t length, const std::string& charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789");

    // File utilities
    /**
     * Read entire file into string
     * @param filename Path to file
     * @return File contents, empty if error
     */
    static std::string read_file(const std::string& filename);

    /**
     * Write string to file
     * @param filename Path to file
     * @param content Content to write
     * @return true if successful
     */
    static bool write_file(const std::string& filename, const std::string& content);

    /**
     * Check if file exists
     * @param filename Path to file
     * @return true if file exists
     */
    static bool file_exists(const std::string& filename);

private:
    // Base64 encoding tables
    static const std::string base64_chars_;
    static bool is_base64(unsigned char c);
};

} // namespace devb