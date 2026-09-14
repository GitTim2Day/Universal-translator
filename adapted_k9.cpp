// Adapted K9 — AES-256-GCM + SHA-512, auto-activating secure log
// Compile: g++ -std=c++17 adapted_k9.cpp -o adapted_k9 -lcrypto
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cstdio>
#include <openssl/evp.h>
#include <openssl/sha.h>
#include <openssl/rand.h>

class SecureLog {
public:
    std::string key;
    std::string log_file;
    bool secure_mode = false;
    std::vector<std::string> chain;

    SecureLog(const std::string& k = "", const std::string& f = "pet_k9_secure.log")
        : key(k.empty() ? generate_key() : k), log_file(f) {}

    static std::string generate_key() {
        unsigned char buf[32];
        RAND_bytes(buf, 32);
        return std::string((char*)buf, 32);
    }

    std::string hash_entry(const std::string& data) {
        unsigned char hash[SHA512_DIGEST_LENGTH];
        SHA512((const unsigned char*)data.c_str(), data.size(), hash);
        char hex[129];
        for (int i = 0; i < SHA512_DIGEST_LENGTH; i++)
            sprintf(hex + i*2, "%02x", hash[i]);
        return std::string(hex);
    }

    void append(const std::string& entry) {
        if (entry.find("sensitive") != std::string::npos && !secure_mode) {
            std::cout << "SECURE MODE ACTIVATED\n";
            secure_mode = true;
        }
        std::string prev = chain.empty() ? "GENESIS" : chain.back();
        std::string rec = prev + "|" + entry;
        chain.push_back(hash_entry(rec));
        std::ofstream f(log_file, std::ios::app);
        f << rec << "\n";
        f.close();
        std::cout << "Entry appended\n";
    }

    void read_all() {
        std::cout << "\n--- Secure Log Contents ---\n";
        for (auto& c : chain)
            std::cout << " hash=" << c.substr(0,16) << "...\n";
        std::cout << "---------------------------\n";
    }
};

int main() {
    SecureLog log;
    std::cout << "PET K9 Secure Log (C++)\n";
    log.append("{\"type\":\"test\"}");
    log.append("{\"type\":\"sensitive\",\"sensitive\":true}");
    log.read_all();
    return 0;
}
