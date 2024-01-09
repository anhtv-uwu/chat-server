from Crypto.Cipher import AES
# Import RSA
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Import the hashing library
import hashlib
# Import the base64 encoding library
import base64
# Import secure random generator
import os

# Build a encryption and decryption function such that a key is encryption from rsa and then used to encrypt the message
# Form of encrypted message is: base64[RSA encrypted key].base64[AES encrypted message]

def encrypt(message: bytes, public_key: bytes) -> str:
    # Create a random key for AES
    aes_key = os.urandom(32)
    # Create an AES-GCM cipher object
    cipher_aes = AES.new(aes_key, AES.MODE_GCM)
    # Encrypt the message
    ciphertext, tag = cipher_aes.encrypt_and_digest(message)
    # Encrypt the AES key using the public key
    rsa_key = RSA.import_key(public_key)
    cipher_rsa = PKCS1_OAEP.new(rsa_key)
    encrypted_key = cipher_rsa.encrypt(aes_key)
    # Return the encrypted message and the tag, create base64 and concat it by .
    return base64.b64encode(encrypted_key).decode() + '.' + base64.b64encode(ciphertext).decode() + '.' + base64.b64encode(cipher_aes.nonce).decode() + '.' + base64.b64encode(tag).decode()

def decrypt(message: str, private_key: bytes) -> bytes:
    # Decode the message
    encrypted_key, ciphertext, nonce, tag = map(base64.b64decode, message.split('.'))
    # Decrypt the AES key using the private key
    rsa_key = RSA.import_key(private_key)
    cipher_rsa = PKCS1_OAEP.new(rsa_key)
    aes_key = cipher_rsa.decrypt(encrypted_key)
    # Decrypt the message
    cipher_aes = AES.new(aes_key, AES.MODE_GCM, nonce)
    plaintext = cipher_aes.decrypt_and_verify(ciphertext, tag)
    # Return the decrypted message
    return plaintext

def generate_keys():
    # Generate an RSA key pair
    key = RSA.generate(2048)
    # Return the private and public key parts
    return key.export_key(), key.publickey().export_key()