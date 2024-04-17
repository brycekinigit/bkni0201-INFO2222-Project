'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for
from flask_socketio import SocketIO
import db
from models import *
import secrets

import logging

# import cherrypy

# this turns off Flask Logging, uncomment this to turn off Logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)

# don't remove this!!
import socket_routes

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

    if user.password != password:
        return "Error: Password does not match!"

    # BKNI0201 - Changed this
    # return url_for('home', username=request.json.get("username"))
    return url_for('friends', username=request.json.get("username"))

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

    if db.get_user(username) is None:
        db.insert_user(username, password)
        return url_for('home', username=username)
    return "Error: User already exists!"

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# Note - Doesn't do any database access using username, efficient, but allows anyone to be anyone
# home page, where the messaging app is
@app.route("/home")
def home():
    if request.args.get("username") is None:
        abort(404)
    return render_template("home.jinja", username=request.args.get("username"))



# OUR CODE



# Here, we do db request, then check if that is None, so if a non-existent username is input, we just abort
# Template was to check if username request argument was None
@app.route("/friends")
def friends():
    # Just directly accesses entry for "username" from http request
    user = db.get_user(request.args.get("username"))
    if user is None:
        abort(404)
    friends = db.get_friends(user.username)
    friends_string = "<ul>"
    requests_string = "<ul>"
    for i in friends:
        if i.accepted:
            if i.frienda != user.username:
                friends_string += f"<li>{i.frienda}</li>"
            else:
                friends_string += f"<li>{i.friendb}</li>"
        elif i.friendb == user.username:
            requests_string += f"<li>{i.frienda} <button onclick=\"accept({i.id}, '{user.username}');\">Accept</button></li>"
    friends_string += "</ul>"
    return render_template("friends.jinja", username=user.username, friends=friends_string, requests=requests_string)


# Note - Switched from cherrypy to just through socketio, for simplicity and so don't have to type in passphrase twice

# cherrypy.tree.graft(app.wsgi_app, '/')
# cherrypy.config.update({
#     'server.socket_host': '127.0.0.1',
#     'server.socket_port': 5000,
#     'engine.autoreload.on': False,
#     'server.ssl_module': 'builtin',
#     'server.ssl_certificate': 'certs/info2222CA.pem',
#     'server.ssl_private_key': 'certs/info2222CA.key',
# })

if __name__ == '__main__':
    # cherrypy.engine.start()
    # socketio.run(app)
    socketio.run(app, ssl_context=('certs/info2222CA.pem', 'certs/info2222CA.key'))
