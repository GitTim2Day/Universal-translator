import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import json
from datetime import datetime

class SecureLog:
    def __init__(self, master_key=None, log_file="pet_k9_secure.log"):
        self.key = master_key or os.urandom(32)
        self.log_file = log_file
        self.secure_mode = False
        self.chain = []

    def hash_entry(self, data):
        entry = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha512(entry).hexdigest()

    def encrypt(self, data):
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, json.dumps(data).encode(), None)
        return {
            "nonce": nonce.hex(),
            "ciphertext": ciphertext.hex(),
            "hash": self.hash_entry(data)
        }

    def decrypt(self, encrypted_entry):
        if "nonce" not in encrypted_entry or "ciphertext" not in encrypted_entry:
            raise ValueError("Not an encrypted entry")
        aesgcm = AESGCM(self.key)
        nonce = bytes.fromhex(encrypted_entry["nonce"])
        ciphertext = bytes.fromhex(encrypted_entry["ciphertext"])
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        data = json.loads(plaintext.decode())
        if self.hash_entry(data) != encrypted_entry["hash"]:
            raise ValueError("Data has been tampered with!")
        return data

    def append(self, entry):
        if entry.get("sensitive"):
            if not self.secure_mode:
                print("SECURE MODE ACTIVATED — sensitive data detected")
                self.secure_mode = True
        prev_hash = self.chain[-1]["hash"] if self.chain else "GENESIS"
        payload = self.encrypt(entry) if self.secure_mode else entry
        record = {
            "timestamp": datetime.now().isoformat(),
            "prev_hash": prev_hash,
            "payload": payload,
            "hash": self.hash_entry(entry)
        }
        self.chain.append(record)
        with open(self.log_file, "a") as f:
            f.write(json.dumps(record) + "\n")
        print(f"Entry appended at {record['timestamp']}")

    def read_all(self):
        print("\n--- Secure Log Contents ---")
        for rec in self.chain:
            print(f"prev={rec['prev_hash'][:16]}... hash={rec['hash'][:16]}...")
        print("---------------------------\n")

def translate_and_log(audio, target_lang, log):
    if audio is None:
        return "No audio received."
    english = "Hello, how are you?"
    translated = "Bonjour, comment ça va ?" if target_lang == "French" else "Hola, ¿cómo estás?"
    entry = {
        "type": "translation",
        "original": english,
        "target_lang": target_lang,
        "translation": translated,
        "sensitive": False
    }
    log.append(entry)
    return translated

if __name__ == "__main__":
    log = SecureLog(master_key=b"0"*32)
    print(translate_and_log("audio1", "French", log))
    log.append({"type":"test", "sensitive": True, "data": "classified"})
    print("Secure mode:", log.secure_mode)
    log.read_all()