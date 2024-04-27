'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import *
from flask_socketio import SocketIO, join_room, emit, leave_room
import db
from models import *
import secrets
import bcrypt
import logging
import base64
from sys import stdout, stderr

room = Room()

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)



# index page
@app.route("/")
def index():
    return render_template("index.jinja")

# login page
@app.route("/login")
def login():    
    return render_template("login.jinja")

# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password")

    user =  db.get_user(username)
    if user is None:
        return "Error: User does not exist!"
    if not bcrypt.checkpw(password.encode(), user.password_hash):
        return "Error: Incorrect password!"
    session["username"] = username
    return url_for('friends', username=username)

# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)
    username = request.json.get("username")
    password = request.json.get("password")
    password_client_salt = request.json.get("passwordSalt")
    
    # Check username
    error_message = username_error(username)
    if error_message:
        return error_message
    if db.get_user(username):
        return "Error: User already exists!"
    
    # check password
    if (not password) or len(password) < 10:
        return "Error: Password too short."
    # hasspecial = False
    # hascapital = False
    # for i in password:
    #     if not i.isalpha():
    #         hasspecial = True
    #     if i.isupper():
    #         hascapital = True
    # if not hascapital:
    #     return "Error: Password must contain a capital letter."
    # if not hasspecial:
    #     return "Error: Password must contain a non-alphabetic character."
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    password = "Some string to replace the real password"
    db.insert_user(username, hashed_password, password_client_salt)
    session["username"] = username
    return url_for('friends', username=username)
        

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# home page, where the messaging app is
@app.route("/home")
def home():
    username = session_user(session)
    if not username:
        return redirect(url_for("index"))
    # room_id =  room.get_room_id(username)
    # if room_id is None:
    #     room_id = -1
    return render_template("home.jinja", username=username, room_id=-1, partner="")

@app.route("/home/<partner>")
def home_partner(partner):
    username = session_user(session)
    if not username:
        return redirect(url_for("index"))
    return render_template("home.jinja", username=username, room_id=-1, partner=partner)

# Friends list page, where friends are shown and managed
@app.route("/friends")
def friends():
    username = session_user(session)
    if not username:
        return redirect(url_for("index"))
    user = db.get_user(username)
    if user is None:
        return redirect(url_for("signup"))
    friends_list = db.get_rels(username)
    friends = ""
    incoming = ""
    outgoing = ""
    for i in friends_list:
        if i.accepted:
            # put relationship the right way
            if i.frienda != username:
                friends += f"<li><a href=\"{url_for('home')}/{i.frienda}\">{i.frienda}</a></li>"
            else:
                friends += f"<li><a href=\"{url_for('home')}/{i.friendb}\">{i.friendb}</a></li>"
        # If request is to user
        elif i.friendb == username:
            incoming += f"<li>{i.frienda} <button onclick=\"accept_request({i.id});\">Accept</button> <button onclick=\"reject_request({i.id});\">Reject</button></li>"
        # If request is from user
        elif i.frienda == username:
            outgoing += f"<li>{i.friendb} (Pending)"
    return render_template("friends.jinja", username=username, friends=friends, incoming=incoming, outgoing=outgoing)

# Handle accepting a friend request
@app.route("/friends/accept", methods=["POST"])
def friends_accept():
    username = session_user(session)
    if not username:
        return "Error: Not logged in."
    if not request.is_json:
        abort(404)

    friendship_id = request.json.get("friendship_id")
    error_message = db.accept_request(friendship_id)
    if error_message:
        return error_message
    return url_for("friends")

# Handle accepting a friend request
@app.route("/friends/reject", methods=["POST"])
def friends_reject():
    username = session_user(session)
    if not username:
        return "Error: Not logged in."
    if not request.is_json:
        abort(404)

    friendship_id = request.json.get("friendship_id")
    error_message = db.reject_friend(friendship_id)
    if error_message:
        return error_message
    return url_for("friends")

@app.route("/friends/request", methods=["POST"])
def friends_request():
    username = session_user(session)
    if not username:
        return redirect(url_for("index"))
    if not request.is_json:
        abort(404)
    friend = request.json.get("friend_username")
    if username_error(friend):
        return "Error: Invalid username"
    if not db.get_user(friend):
        return f"Error: No user named \"{friend}\"."
    if friend == username:
        return "Error: You cannot befriend yourself"
    # Get all relationships referencing user
    relationships = db.get_rels(username)
    for i in relationships:
        if i.frienda == friend or i.friendb == friend:
            return "Error: Relationship already exists"
    db.insert_friend(username, friend)
    return url_for("friends")



@app.route("/user/client-salt")
def get_password_client_salt():
    username = request.args.get("username")
    if username_error(username):
        return ""
    user = db.get_user(username)
    if not user:
        return ""
    return user.password_client_salt



# when the client connects to a socket
# this event is emitted when the io() function is called in JS
# @socketio.on('connect')
# def connect():
#     username = session_user(session)
#     room_id = room.get_room_id(username)
#     if room_id is None or username is None:
#         return
#     # socket automatically leaves a room on client disconnect
#     # so on client connect, the room needs to be rejoined
#     # join_room(int(room_id))
#     # message_history()
#     # emit("incoming", (f"{username} has connected", "green"), to=int(room_id))
    

# event when client disconnects
# quite unreliable use sparingly
@socketio.on('disconnect')
def disconnect():
    username = session_user(session)
    room_id = room.get_room_id(username)
    if room_id is None or username is None:
        return
    room.leave_room(username)
    emit("incoming", (f"{username} has left the room. (disconnected)", "red"), to=room_id)

# send message event handler
@socketio.on("send")
def send(message_data):
    username = session_user(session)
    room_id = room.get_room_id(username)
    friend_id = room.get_friend_from_room(room_id)
    emit("incomingEncrypted", (0, f"{username}: ", message_data), to=room_id)
    db.log_message(friend_id, username, message_data)
    
    
@socketio.on("publicKey")
def forward_key(key):
    username = session_user(session)
    room_id = room.get_room_id(username)
    emit("publicKey", key, to=room_id, include_self=False)
    print("Forwarded a public key")

# Not needed as server handles requesting public keys automatically
# @socketio.on("publicKeyRequest")
# def request_key():
#     username = session_user(session)
#     room_id = room.get_room_id(username)
#     emit("publicKeyRequest", to=room_id, include_self=False)
#     print("Forwarded a request for public key")
    
@socketio.on("roomKey")
def store_key(key):
    username = session_user(session)
    room_id = room.get_room_id(username)
    friend_id = room.get_friend_from_room(room_id)
    key["encryptedKey"] = bytesToString(key["encryptedKey"])
    key["iv"] = bytesToString(key["iv"])
    db.store_room_key(username, friend_id, key)
    
# join room event handler
# sent when the user joins a room
@socketio.on("join")
def join(receiver_name):
    response = {
        "success": 0,
        "hasKey": 0
    }
    sender_name = session_user(session)
    receiver = db.get_user(receiver_name)
    if receiver is None:
        response["error"] = "Error: Unknown receiver!"
        return response
    sender = db.get_user(sender_name)
    if sender is None:
        response["error"] = "Error: Unknown sender!"
        return response
    
    # Check if users are friends
    friend_id = db.friendship_id(sender_name, receiver_name)
    if friend_id is not None:
        # If there isn't a room for this pair, create one
        room_id = room.get_friend_room_id(friend_id)
        if room_id is None:
            room_id = room.create_friend_room(friend_id)
        # If the sender already has a key stored in the database
        if (sender.room_keys is not None) and (str(friend_id) in sender.room_keys):
            key = sender.room_keys[str(friend_id)]
            response["key"] = {
                "encryptedKey": stringToBytes(key["encryptedKey"]),
                "iv": stringToBytes(key["iv"]),
            }
            response["hasKey"] = 1
        response["room_id"] = room_id
        room.join_room(sender_name, room_id)
        join_room(room_id)
        # emit to everyone in the room except the sender
        emit("incoming", (f"{sender_name} has joined the room.", "green"), to=room_id, include_self=False)
        # emit to just the sender
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"))
        
        if response["hasKey"] == 0:
            # Ask other people in the room for their public keys
            emit("publicKeyRequest", to=room_id, include_self=False)
        response["success"] = 1
        print("Returning join response")
        return response
    response["error"] = "Error: Receiver is not a friend"
    return response

# leave room event handler
@socketio.on("leave")
def leave():
    username = session_user(session)
    room_id = room.get_room_id(username)
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    leave_room(room_id)
    room.leave_room(username)

@socketio.on("history")
def message_history(partner):
    username = session_user(session)
    if not username:
        return
    print(f"Sending history for {username}")
    room_id = room.get_room_id(username)
    friend_id = room.get_friend_from_room(room_id)
    for message in db.get_messages(friend_id):
        # print("Sent a past message")
        message.data["message"] = stringToBytes(message.data["message"])
        message.data["iv"] = stringToBytes(message.data["iv"])
        emit("incomingEncrypted", (1, f"{message.username}: ", message.data))

def session_user(session):
    '''
    Returns the username of the currently logged in user, or None if authentication unsuccessful
    '''
    if "username" in session.keys():
        return session["username"]
    else:
        return None

def username_error(username):
    '''
    Returns an empty string if the username is valid, or an appropriate error message if not.
    Allowed non-alphabetic characters are: 0123456789,.?!@#$%^&*()-_=+
    notably excluding html and json syntax, and backslash for escape characters </>, {"":[]}, \\
    '''
    if len(username) < 3:
        return "Error: Username too short."
    allowed_special_chars = "0123456789,.?!@#$%^&*()-_=+"
    for i in username:
        if not (i.isalpha() or i in allowed_special_chars):
            return "Error: Username contains invalid characters"
    return ""

def bytesToString(text: bytes):
    return base64.b64encode(text).decode("utf-8")
    
def stringToBytes(text: str):
    return base64.b64decode(text.encode("utf-8"))

if __name__ == '__main__':
    # socketio.run(app)
    socketio.run(app, ssl_context=('certs/info2222CA.pem', 'certs/info2222CA.key'))
