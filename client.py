# client.py
import socket
import json
import threading

def receive_messages():
    while True:
        message = client_socket.recv(1024)
        if not message:
            break
        message = json.loads(message.decode())
        # print(message)
        if message['mode'] == 'message':
            print(f"Received message from {message['id']}: {message['message']}")
        if message['mode'] == 'notification':
            print(f"Notification: {message['message']}")

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 8089))

# Set the client ID
client_id = input("Enter your username: ")
client_socket.send(client_id.encode())

# Start a new thread to receive messages from the server
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# Send messages to other clients
while True:
    try:
        sender_id = input("Enter recipient username: ")
        message = input("Enter message: ")
        message = {'mode': 'message', 'send_to': sender_id, 'message': message}
        client_socket.send(json.dumps(message).encode())
    except KeyboardInterrupt:
        # Close the connection when the user presses Ctrl+C
        client_socket.close()
        break