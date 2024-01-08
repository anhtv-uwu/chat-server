# server.py
import socket
import threading
import json
import sys

client_id_map = {}
client_socket_map = {}
def handle_client(client_socket, client_address):

    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            message = json.loads(message.decode())
            if message['mode'] == 'message':
                print(f"Received message from {client_socket_map[client_socket]} to {message['send_to']}: {message['message']}")
                # Send the message to the recipient client
                send_message = {'mode': 'message', 'id': client_socket_map[client_socket], 'message': message['message']}
                # Check send_to is in client_id_map
                if message['send_to'] in client_id_map:
                    client_id_map[message['send_to']].send(json.dumps(send_message).encode())
                else:
                    print(f"Client {message['send_to']} not found")


            if message['mode'] == 'auth_pub':
                print(f"Received public key from {message['id']}")
                # Send the message to the recipient client
        except Exception:
            print(f"Client {client_socket_map[client_socket]} disconnected")
            break


    # Remove the client from the list of connected clients
    client_id_map.pop(client_socket_map[client_socket])
    client_socket_map.pop(client_socket)
    client_socket.close()


def accept_clients():
    while True:
        client_socket, client_address = server_socket.accept()
        # Receive the client's ID
        client_id = client_socket.recv(1024).decode()
        print(f"Client {client_id} connected")
        # Add the client to the list of connected clients
        client_id_map[client_id] = client_socket
        client_socket_map[client_socket] = client_id
        print(f"Accepted connection from {client_address}")
        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()



# Create a TCP socket and bind it to a port
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 8089))
server_socket.listen()

clients = []
print("Server started. Listening for connections...")

# Accept incoming client connections
accept_thread = threading.Thread(target=accept_clients)
accept_thread.start()

#

