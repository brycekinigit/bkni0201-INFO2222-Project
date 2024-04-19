'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import *
from flask_socketio import SocketIO
import db
from models import *
import secrets
import bcrypt
# don't remove this, even though not accessed!!!
import socket_routes
import logging

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
    if not bcrypt.checkpw(password.encode(), user.password):
        return "Error: Incorrect password!"
    session["username"] = username
    # Do we want to redirect to friends or home?
    return url_for('friends')

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
    
    # Check username
    error_message = username_error(username)
    if error_message:
        return error_message
    if db.get_user(username):
        return "Error: User already exists!"
    
    # check password
    if len(password) < 6:
        return "Error: Password too short."
    hasspecial = False
    hascapital = False
    for i in password:
        if not i.isalpha():
            hasspecial = True
        if i.isupper():
            hascapital = True
    if not hascapital:
        return "Error: Password must contain a capital letter."
    if not hasspecial:
        return "Error: Password must contain a non-alphabetic character."
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    password = "Some string to replace the real password"
    db.insert_user(username, hashed_password)
    session["username"] = username
    return url_for('home', username=username)
        

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
    return render_template("home.jinja", username=username)

# Friends list page, where friends are shown and managed
@app.route("/friends")
def friends():
    username = session_user(session)
    if not username:
        return redirect(url_for("index"))
    user = db.get_user(username)
    if user is None:
        return redirect(url_for("signup"))
    friends_list = db.get_friends(username)
    friends = ""
    incoming = ""
    outgoing = ""
    for i in friends_list:
        if i.accepted:
            # put relationship the right way
            if i.frienda != username:
                friends += f"<li>{i.frienda}</li>"
            else:
                friends += f"<li>{i.friendb}</li>"
        # If request is to user
        elif i.friendb == username:
            incoming += f"<li>{i.frienda} <button onclick=\"accept_request({i.id});\">Accept</button></li>"
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
    # TODO: Check if friend relationship exists
    # TODO: Append new relationship to database
    return url_for("friends")


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
    Returns an empty string if the username is valid, or an appropriate error message if not
    '''
    if len(username) < 3:
        return "Error: Username too short."
    valid_characters = "?!@#$%^&*()-_+"
    for i in username:
        if not (i.isalpha() or i.isnumeric or i in valid_characters):
            return "Error: Username contains invalid characters"
    return ""

if __name__ == '__main__':
    # socketio.run(app)
    socketio.run(app, ssl_context=('certs/info2222CA.pem', 'certs/info2222CA.key'))
