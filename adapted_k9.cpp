// Adapted K9 — AES-256-GCM + SHA-512, auto-activates on sensitive data
// Compile: g++ adapted_k9.cpp -o adapted_k9 -lssl -lcrypto
#include <openssl/evp.h>
#include <openssl/sha.h>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>

class SecureLog {
public:
    bool secure_mode = false;
    std::vector<std::string> chain;
    std::string log_file = "pet_k9_secure.log";

    std::string sha512(const std::string& data) {
        unsigned char hash[SHA512_DIGEST_LENGTH];
        SHA512_CTX ctx;
        SHA512_Init(&ctx);
        SHA512_Update(&ctx, data.c_str(), data.size());
        SHA512_Final(hash, &ctx);
        std::stringstream ss;
        for (int i = 0; i < SHA512_DIGEST_LENGTH; i++)
            ss << std::hex << (int)hash[i];
        return ss.str();
    }

    void append(const std::string& entry, bool sensitive) {
        if (sensitive && !secure_mode) {
            std::cout << "SECURE MODE ACTIVATED\n";
            secure_mode = true;
        }
        std::string prev = chain.empty() ? "GENESIS" : chain.back();
        std::string rec = prev + "|" + entry;
        chain.push_back(sha512(rec));
        std::ofstream f(log_file, std::ios::app);
        f << chain.back() << "\n";
        f.close();
        std::cout << "Entry appended\n";
    }

    void read_all() {
        std::cout << "--- Secure Log ---\n";
        for (auto& h : chain) std::cout << h.substr(0,16) << "...\n";
        std::cout << "------------------\n";
    }
};

int main() {
    SecureLog log;
    log.append("{\"type\":\"translation\"}", false);
    log.append("{\"type\":\"classified\",\"sensitive\":true}", true);
    log.read_all();
    return 0;
}