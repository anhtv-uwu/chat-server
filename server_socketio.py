# server.py
import socketio
import eventlet
import json

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

# Allow CORS


client_id_map = {}
pubkey_map = {}
sid_map = {}


@sio.event
def connect(sid, environ):
    print('connect ', sid)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)
    # Remove client from map
    if sid in client_id_map:
        del sid_map[client_id_map[sid]]
        del pubkey_map[client_id_map[sid]]
        del client_id_map[sid]
        
        print(f"Client {sid} disconnected")

@sio.event
def message(sid, data):
    print(f"Received message from {client_id_map[sid]} to {data['send_to']}: {data['message']}")
    if data['send_to'] in sid_map:
        sio.emit('message', {'id': client_id_map[sid], 'message': data['message']}, room=sid_map[data['send_to']])
        # sio.emit('notification', {'message': 'Message sent to ' + data['send_to']}, room=sid)
    else:
        sio.emit('notification', {'message': 'Client ' + data['send_to'] + ' not found'}, room=sid)

@sio.event
def auth_userid(sid, data):
    # print(f"{data['id']} send auth request")
    if data['id'] not in sid_map:
        client_id_map[sid] = data['id']
        sid_map[data['id']] = sid
        # print(f"Client {data['id']} connected")
        sio.emit('auth_userid', {'status': True, 'message': 'Connected to server'}, room=sid)
    else:
        # print("Address already connected")
        sio.emit('auth_userid', {'status': False, 'message': 'Already connected'}, room=sid)
        # sio.disconnect(sid)


@sio.event
def auth_pub(sid, data):
    if data['pubkey']:
        pubkey_map[client_id_map[sid]] = data['pubkey']
        # print(f"Client {sid} sent public key")
        # print(f"Public key: {data['pubkey']}")
        sio.emit('notification', {'message': 'Received public key'}, room=sid)
    else:
        sio.emit('notification', {'message': 'No public key received'}, room=sid)

@sio.event
def get_pubkey(sid, data):
    if data['id'] in pubkey_map:
        pubkey = pubkey_map[data['id']]
        # print(f"Client {sid} requested public key of {data['id']}")
        sio.emit('get_pubkey', {'id': data['id'], 'pubkey': pubkey, 'status': 'success'}, room=sid)
    else:
        sio.emit('get_pubkey', {'id': data['id'], 'status': 'error'}, room=sid)

@sio.event
def get_all_pubkey(sid):
    # print(f"Client {sid} requested all public key")
    sio.emit('get_all_pubkey', {'pubkey_map': pubkey_map, 'status': 'success'}, room=sid)

@sio.event
def get_useronline(sid):
    # print(f"Client {sid} requested online users")
    # sio.emit('get_useronline', {'users': list(client_id_map.values()), 'status': 'success'}, room=sid)
    # Get user except sender
    list_user = list(client_id_map.values())
    list_user.remove(client_id_map[sid])
    sio.emit('get_useronline', {'users': list_user, 'status': 'success'}, room=sid)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('localhost', 8089)), app)