from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import os

def generate_rsa_keys(output_dir, key_size=2048):
    os.makedirs(output_dir, exist_ok=True)
    key = RSA.generate(key_size)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    with open(os.path.join(output_dir, 'private.pem'), 'wb') as f:
        f.write(private_key)
    with open(os.path.join(output_dir, 'public.pem'), 'wb') as f:
        f.write(public_key)

def sign_file(filepath, private_key_path, output_signature_path):
    with open(filepath, 'rb') as f:
        data = f.read()
    key = RSA.import_key(open(private_key_path).read())
    hash_obj = SHA256.new(data)
    signature = pkcs1_15.new(key).sign(hash_obj)
    with open(output_signature_path, 'wb') as f:
        f.write(signature)

def verify_signature(filepath, signature_path, public_key_path):
    with open(filepath, 'rb') as f:
        data = f.read()
    with open(signature_path, 'rb') as f:
        signature = f.read()
    key = RSA.import_key(open(public_key_path).read())
    hash_obj = SHA256.new(data)
    try:
        pkcs1_15.new(key).verify(hash_obj, signature)
        return True
    except (ValueError, TypeError):
        return False
