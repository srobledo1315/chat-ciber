import base64
import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class CryptoEngine:
    def __init__(self):
        # Generación de par de claves RSA para la instancia
        self.rsa_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.rsa_public_key = self.rsa_private_key.public_key()
        # Clave simétrica fija pre-compartida (Simulación AES directo)
        self.aes_preshared_key = b"ThisIsASecretPreSharedKey1234567"

    def get_public_key_pem(self) -> str:
        pem = self.rsa_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')

    @staticmethod
    def load_public_key_pem(pem_str: str):
        return serialization.load_pem_public_key(pem_str.encode('utf-8'))

    # --- AES SIMÉTRICO ---
    def encrypt_aes(self, plaintext: str, key: bytes = None) -> dict:
        k = key if key else self.aes_preshared_key
        aesgcm = AESGCM(k)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        return {
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8')
        }

    def decrypt_aes(self, payload: dict, key: bytes = None) -> str:
        k = key if key else self.aes_preshared_key
        aesgcm = AESGCM(k)
        nonce = base64.b64decode(payload["nonce"])
        ciphertext = base64.b64decode(payload["ciphertext"])
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted.decode('utf-8')

    # --- RSA ASIMÉTRICO ---
    def encrypt_rsa(self, plaintext: str, target_pub_key) -> str:
        ciphertext = target_pub_key.encrypt(
            plaintext.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(ciphertext).decode('utf-8')

    def decrypt_rsa(self, ciphertext_b64: str) -> str:
        ciphertext = base64.b64decode(ciphertext_b64)
        decrypted = self.rsa_private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted.decode('utf-8')

    # --- CIFRADO HÍBRIDO ---
    def encrypt_hybrid(self, plaintext: str, target_pub_key) -> dict:
        ephemeral_aes_key = AESGCM.generate_key(bit_length=256)
        aes_data = self.encrypt_aes(plaintext, ephemeral_aes_key)
        
        enc_aes_key = target_pub_key.encrypt(
            ephemeral_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return {
            "encrypted_key": base64.b64encode(enc_aes_key).decode('utf-8'),
            "nonce": aes_data["nonce"],
            "ciphertext": aes_data["ciphertext"]
        }

    def decrypt_hybrid(self, payload: dict) -> str:
        enc_aes_key = base64.b64decode(payload["encrypted_key"])
        ephemeral_aes_key = self.rsa_private_key.decrypt(
            enc_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return self.decrypt_aes(payload, ephemeral_aes_key)