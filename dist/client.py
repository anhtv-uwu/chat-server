# client.py
import socket
import json
import threading
import libcrypto
import sys

MAX_SIZE = 1024

my_privkey, my_pubkey = libcrypto.generate_keys()

def get_pubkey(client_id):
    message = {'mode': 'get_pubkey', 'id': client_id}
    client_socket.send(json.dumps(message).encode())
    response = client_socket.recv(MAX_SIZE)
    response = json.loads(response.decode())
    if response['status'] == 'success':
        return response['pubkey']
    else:
        return None

def receive_messages():
    while True:
        message = client_socket.recv(MAX_SIZE)
        if not message:
            break
        message = json.loads(message.decode())
        # print(message)
        if message['mode'] == 'message':
            print(f"Received message from {message['id']}: {libcrypto.decrypt(message['message'], my_privkey)}")
        if message['mode'] == 'notification':
            print(f"Notification: {message['message']}")

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 8089))

# Set the client ID
client_id = input("Enter your username: ")
client_socket.send(client_id.encode())
success_message = client_socket.recv(MAX_SIZE)
if not success_message:
    print("Server error")
    sys.exit(1)

print("Connected to server")

# Send the public key to the server
key = {'mode': 'auth_pub', 'pubkey': my_pubkey.decode()}
client_socket.send(json.dumps(key).encode())

# Start a new thread to receive messages from the server
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# Send messages to other clients
while True:
    try:
        sender_id = input("Enter recipient username: ")
        pubkey = get_pubkey(sender_id)
        if not pubkey:
            print(f"Could not get public key of {sender_id}")
            continue
        message = input("Enter message: ")
        message = libcrypto.encrypt(message.encode(), pubkey)
        message = {'mode': 'message', 'send_to': sender_id, 'message': message}
        client_socket.send(json.dumps(message).encode())
    except KeyboardInterrupt:
        # Close the connection when the user presses Ctrl+C
        client_socket.close()
        break