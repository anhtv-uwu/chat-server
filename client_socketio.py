# client.py
import socketio
import json
import libcrypto
import sys
import time

my_privkey, my_pubkey = libcrypto.generate_keys()

AUTH = False
USERNAME = None

UserOnline = []
pubkey_map = {}

sio = socketio.Client()

@sio.event
def connect():
    print('Connected to server')
    sio.emit('auth_userid', {'id': USERNAME})
    while not AUTH:
        time.sleep(0.1)
    sio.emit('auth_pub', {'pubkey': my_pubkey})

@sio.event
def disconnect():
    print('Disconnected from server')

@sio.event
def auth_userid(data):
    global AUTH
    if data['status']:
        print(data['message'])
        AUTH = True
    else:
        print(data['message'])
        sio.disconnect()

@sio.event
def message(data):
    print(f"Received message from {data['id']}: {libcrypto.decrypt(data['message'], my_privkey)}")

@sio.event
def notification(data):
    print(f"Notification: {data['message']}")

@sio.event
def get_pubkey(data):
    # print(data)
    if data['status'] == 'success':
        pubkey_map[data['id']] = data['pubkey']

@sio.event
def get_useronline(data):
    global UserOnline
    UserOnline = data
    print(UserOnline)

def send_message(client_id, message):
    # Request pubkey
    if client_id not in pubkey_map:
        print("Getting public key")
        sio.emit('get_pubkey', {'id': client_id})
        # Wait for pubkey
        while client_id not in pubkey_map:
            # print("Waiting for public key")
            time.sleep(0.1)
    # Encrypt message
    pubkey = pubkey_map[client_id]
    encrypted_message = libcrypto.encrypt(message.encode(), pubkey)
    # Send message
    sio.emit('message', {'send_to': client_id, 'message': encrypted_message})

def get_useronline():
    sio.emit('get_useronline')

    
if __name__ == '__main__':
    USERNAME = input("Enter your username: ")
    sio.connect('http://localhost:8089')
    
    while True:
        recipient_id = input("Enter the recipient's ID: ")
        message = input("Enter your message: ")
        send_message(recipient_id, message)