from flask import Flask, request, jsonify
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import os
import requests
import time

app = Flask(__name__)

# --- Encryption functions with fixed IV (all zeros) ---

def encrypt_aes(data, key):
    # IV is now 16 bytes of zeros
    iv = b'\x00' * 16
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    # PKCS7 padding: pad_len is between 1 and 16
    pad_len = 16 - (len(data) % 16)
    padded_data = data + bytes([pad_len] * pad_len)
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    # Prepend IV (even if constant) to match decryption format
    return base64.b64encode(iv + ciphertext).decode('utf-8')

def decrypt_aes(encrypted_data, key):
    encrypted_data = base64.b64decode(encrypted_data)
    iv =  b'\x00' * 16
    ciphertext = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(ciphertext) + decryptor.finalize()
    pad_len = decrypted[-1]
    return decrypted[:-pad_len]

# --- File handling utilities ---

def load_key():
    key_path = 'encryption.key'
    if os.path.exists(key_path):
        with open(key_path, 'rb') as f:
            return f.read()
    else:
        return b'test'  # Default key (insecure - replace with proper key management)

def load_bot_token():
    token_path = 'bot.token'
    if os.path.exists(token_path):
        with open(token_path, 'r') as f:
            return f.read().strip()
    return 'default_token'  # Replace with your actual bot token

# --- Endpoints ---

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    provided_id = data.get('id', '')
    if not provided_id:
        return jsonify({'error': 'No id provided'}), 400

    token = load_bot_token()
    # Call Telegram getUpdates endpoint to fetch the latest messages
    getupdates_url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        response = requests.get(getupdates_url)
        updates = response.json()
    except Exception as e:
        return jsonify({'error': 'Failed to fetch updates from Telegram', 'details': str(e)}), 500

    # Search through the updates for a message where the text matches provided_id
    real_chat_id = None
    for update in updates.get('result', []):
        message = update.get('message', {})
        text = message.get('text', '')
        if text == provided_id:
            # Use the chat id from the message (which is what you'll need to send messages)
            real_chat_id = str(message.get('chat', {}).get('id', ''))
            break

    if not real_chat_id:
        return jsonify({'error': 'No matching message found for provided id'}), 404

    # Encrypt the real chat id
    key = load_key()
    encrypted_id = encrypt_aes(real_chat_id.encode(), key)
    return jsonify({'encodedID': encrypted_id})

@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json()
    encoded_id = data.get('encodedID', '')
    retries = data.get('notifyRetries', 1)
    
    key = load_key()
    try:
        chat_id = decrypt_aes(encoded_id, key).decode()
    except Exception as e:
        return jsonify({'error': 'Invalid encodedID', 'details': str(e)}), 400

    token = load_bot_token()
    message = "Your Solo Shuffle is ready."
    
    for _ in range(retries):
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {'chat_id': chat_id, 'text': message}
        requests.get(url, params=params)
        time.sleep(1)
    
    return jsonify({'status': 'notifications sent'})

if __name__ == '__main__':
    app.run(debug=True)
