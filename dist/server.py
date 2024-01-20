# server.py
import socket
import threading
import json
import sys

client_id_map = {}
client_socket_map = {}
pubkey_map = {}
MAX_SIZE = 1024

def handle_client(client_socket, client_address):

    while True:
        try:
            message = client_socket.recv(MAX_SIZE)
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
                    success_message = {'mode': 'notification', 'message': 'Message sent to ' + message['send_to']}
                    client_socket.send(json.dumps(success_message).encode())

                else:
                    error_message = {'mode': 'notification', 'message': 'Client ' + message['send_to'] + ' not found'}
                    client_socket.send(json.dumps(error_message).encode())
                    print(f"Client {message['send_to']} not found")

        
            if message['mode'] == 'auth_pub':
                if message['pubkey']:
                    client_id = client_socket_map[client_socket]
                    pubkey_map[client_id] = message['pubkey']
                    print(f"Client {client_id} sent public key")
                    success_message = {'mode': 'notification', 'message': 'Received public key'}
                    client_socket.send(json.dumps(success_message).encode())
                else:
                    error_message = {'mode': 'notification', 'message': 'No public key received'}
                    client_socket.send(json.dumps(error_message).encode())
            
            if message['mode'] == 'get_pubkey':
                if message['id'] in pubkey_map:
                    pubkey = pubkey_map[message['id']]
                    print(f"Client {client_socket_map[client_socket]} requested public key of {message['id']}")
                    success_message = {'mode': 'get_pubkey', 'id': message['id'], 'pubkey': pubkey, 'status': 'success'}
                    client_socket.send(json.dumps(success_message).encode())
                else:
                    error_message = {'mode': 'get_pubkey', 'id': message['id'], 'status': 'error'}
                    client_socket.send(json.dumps(error_message).encode())
                    
                
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
        client_id = client_socket.recv(MAX_SIZE).decode()
        # Check if the client ID is already in use
        if client_id in client_id_map:
            print(f"Client {client_id} already connected")
            client_socket.send("Client ID already in use".encode())
            client_socket.close()
            continue
        print(f"Client {client_id} connected")
        # Send that the client has connected successfully
        client_socket.send("Connected successfully".encode())
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


