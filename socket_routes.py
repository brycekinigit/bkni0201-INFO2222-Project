'''
socket_routes
file containing all the routes related to socket.io
'''


from flask_socketio import join_room, emit, leave_room
from flask import request, session

try:
    from __main__ import socketio
except ImportError:
    from app import socketio

from models import Room

import db
from utils import *

room = Room()

# when the client connects to a socket
# this event is emitted when the io() function is called in JS


# event when client disconnects
# quite unreliable use sparingly
@socketio.on('disconnect')
def disconnect():
    username = session_user(session)
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    emit("incoming", (f"{username} has disconnected", "red"), to=int(room_id))

# send message event handler
@socketio.on("send")
def send(message):
    username = session_user(session)
    room_id = room.get_room_id(username)
    emit("incoming", (f"{username}: {message}"), to=room_id)
    
# join room event handler
# sent when the user joins a room
@socketio.on("join")
def join(sender_name, receiver_name):
    # sender_name = session_user(session)
    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver!"
    
    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"

    room_id = room.get_room_id(receiver_name)

    # if the user is already inside of a room 
    if room_id is not None:
        
        room.join_room(sender_name, room_id)
        join_room(room_id)
        # emit to everyone in the room except the sender
        emit("incoming", (f"{sender_name} has joined the room.", "green"), to=room_id, include_self=False)
        # emit only to the sender
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"))
        return room_id

    # if the user isn't inside of any room, 
    # perhaps this user has recently left a room
    # or is simply a new user looking to chat with someone
    room_id = room.create_room(sender_name, receiver_name)
    join_room(room_id)
    emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"), to=room_id)
    return room_id

# leave room event handler
@socketio.on("leave")
def leave(room_id):
    username = session_user(session)
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    leave_room(room_id)
    room.leave_room(username)