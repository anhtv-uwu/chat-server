# server.py
import socketio
import eventlet
import json

sio = socketio.Server()
app = socketio.WSGIApp(sio)

client_id_map = {}
pubkey_map = {}
sid_map = {}


@sio.event
def connect(sid, environ):
    print('connect ', sid)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

@sio.event
def message(sid, data):
    print(f"Received message from {client_id_map[sid]} to {data['send_to']}: {data['message']}")
    if data['send_to'] in sid_map:
        sio.emit('message', {'id': client_id_map[sid], 'message': data['message']}, room=sid_map[data['send_to']])
        sio.emit('notification', {'message': 'Message sent to ' + data['send_to']}, room=sid)
    else:
        sio.emit('notification', {'message': 'Client ' + data['send_to'] + ' not found'}, room=sid)

@sio.event
def auth_userid(sid, data):
    if data['id'] not in client_id_map:
        client_id_map[sid] = data['id']
        sid_map[data['id']] = sid
        print(f"Client {data['id']} connected")
        sio.emit('auth_userid', {'status': True, 'message': 'Connected to server'}, room=sid)
    else:
        sio.emit('auth_userid', {'status': False, 'message': 'Already connected'}, room=sid)
        sio.disconnect(sid)


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
        print(f"Client {sid} requested public key of {data['id']}")
        sio.emit('get_pubkey', {'id': data['id'], 'pubkey': pubkey, 'status': 'success'}, room=sid)
    else:
        sio.emit('get_pubkey', {'id': data['id'], 'status': 'error'}, room=sid)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('localhost', 8089)), app)