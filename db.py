'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import *
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from models import *
from app import bytesToString, stringToBytes

from pathlib import Path

# creates the database directory
Path("database") \
    .mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=True)

# initializes the database
Base.metadata.create_all(engine)

# inserts a user to the database
def insert_user(username: str, password_hash: bytes, password_client_salt: str):
    with Session(engine) as session:
        user = User(
            username=username,
            password_hash=password_hash,
            password_client_salt = password_client_salt,
        )
        session.add(user)
        session.commit()

# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)



def get_rels(username):
    with Session(engine) as session:
        result = session.execute(select(Friend).where(or_(Friend.frienda == username, Friend.friendb == username))).all()
        return [row[0] for row in result]
        # resulta = session.execute(select(Friend).where(Friend.frienda == username)).all()
        # resultb = session.execute(select(Friend).where(Friend.friendb == username)).all()
        # return [row[0] for row in resulta] + [row[0] for row in resultb]

def friendship_id(frienda, friendb):
    with Session(engine) as session:
        result = session.execute(select(Friend).where(
            and_(
                Friend.accepted, or_(
                    and_(Friend.frienda == frienda, Friend.friendb == friendb),
                    and_(Friend.frienda == friendb, Friend.friendb == frienda)
                )
            )
        )).first()
        if result:
            return result[0].id
        else:
            return None

def accept_request(id):
    with Session(engine) as session:
        result = session.get(Friend, id)
        if result:
            result.accepted = True
            session.commit()
            return
        return f"Error: Couldn't find request {id}"

def store_room_key(username, room_id, key):
    with Session(engine) as session:
        user = session.get(User, username)
        if user is None:
            return "Error: User not found"
        if user.room_keys is None:
            user.room_keys = {}
        if room_id in user.room_keys:
            return "Error, key already set"
        user.room_keys[room_id] = key
        session.commit()

def reject_friend(id):
    with Session(engine) as session:
        result = session.get(Friend, id)
        if result:
            session.delete(result)
            session.commit()
            return
        return f"Error: Couldn't find request {id}"

def insert_friend(frienda, friendb):
    with Session(engine) as session:
        friendship = Friend(frienda=frienda, friendb=friendb, accepted=False)
        session.add(friendship)
        session.commit()
        
def get_messages(friendship_id):
    with Session(engine) as session:
        result = session.execute(select(Message).where(Message.friendship_id == friendship_id)).all()
        return [row[0] for row in result]
    
def log_message(friend_id, username, message_data):
    with Session(engine) as session:
        # We encode in base 64, then text to safely store in JSON
        message_data["message"] = bytesToString(message_data["message"])
        message_data["iv"] = bytesToString(message_data["iv"])
        message = Message(
            friendship_id=friend_id,
            username=username,
            data=message_data
        )
        session.add(message)
        session.commit()

if __name__ == "__main__":
    with Session(engine) as session:
        session.add(Friend(id=1, frienda="alice", friendb="anne", accepted=True))
        session.add(Friend(id=2, frienda="alice", friendb="abby", accepted=True))
        session.add(Friend(id=3, frienda="alice", friendb="anya", accepted=True))
        session.add(Friend(id=4, frienda="bob", friendb="alice", accepted=False))
        session.add(Friend(id=5, frienda="brian", friendb="alice", accepted=False))
        session.add(Friend(id=6, frienda="alice", friendb="carol", accepted=False))
        session.add(Friend(id=7, frienda="alice", friendb="charles", accepted=False))
        session.add(Message(id=1, friendship_id=2, data={"message": "This is a message"}))
        session.add(Message(id=2, friendship_id=2, data="{message: 'This is how data should be'}"))
        session.add(Message(id=3, friendship_id=1, data={"data": "This is somebody elses message"}))
        session.commit()
    result = get_messages(2)
    print(result[0].data, type(result[0].data))
    print(result[1].data, type(result[1].data))