#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <ctime>
#include <iomanip>
#include <sstream>
#include <openssl/sha.h>
#include <openssl/evp.h>
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
        std::string s;
        for (int i = 0; i < 32; i++) s += buf[i];
        return s;
    }

    std::string sha512(const std::string& data) {
        unsigned char hash[SHA512_DIGEST_LENGTH];
        SHA512_CTX ctx;
        SHA512_Init(&ctx);
        SHA512_Update(&ctx, data.c_str(), data.size());
        SHA512_Final(hash, &ctx);
        std::stringstream ss;
        for (int i = 0; i < SHA512_DIGEST_LENGTH; i++)
            ss << std::hex << std::setw(2) << std::setfill('0') << (int)hash[i];
        return ss.str();
    }

    void append(const std::string& entry, bool sensitive) {
        if (sensitive && !secure_mode) {
            std::cout << "SECURE MODE ACTIVATED\n";
            secure_mode = true;
        }
        std::string prev = chain.empty() ? "GENESIS" : chain.back();
        std::string h = sha512(entry);
        chain.push_back(h);
        std::ofstream f(log_file, std::ios::app);
        f << prev << "|" << h << "\n";
        f.close();
        std::cout << "Entry appended\n";
    }

    void read_all() {
        std::cout << "\n--- Log ---\n";
        for (auto& c : chain) std::cout << c.substr(0,16) << "...\n";
        std::cout << "-----------\n";
    }
};

int main() {
    SecureLog log;
    log.append("test1", false);
    log.append("sensitive", true);
    log.read_all();
    return 0;
}