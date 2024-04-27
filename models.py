'''
models
defines sql alchemy data models
also contains the definition for the room class used to keep track of socket.io rooms

Just a sidenote, using SQLAlchemy is a pain. If you want to go above and beyond, 
do this whole project in Node.js + Express and use Prisma instead, 
Prisma docs also looks so much better in comparison

or use SQLite, if you're not into fancy ORMs (but be mindful of Injection attacks :) )
'''

from sqlalchemy import String, BINARY, ForeignKey, Integer, Boolean, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Dict

# data models
class Base(DeclarativeBase):
    pass

# model to store user information
class User(Base):
    __tablename__ = "user"
    username: Mapped[str] = mapped_column(String, primary_key=True)
    password_hash: Mapped[bytes] = mapped_column(BINARY)
    password_client_salt: Mapped[str] = mapped_column(String)
    room_keys = mapped_column(JSON)

class Friend(Base):
    __tablename__ = "friend"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    frienda: Mapped[str] = mapped_column(String)
    friendb: Mapped[str] = mapped_column(String)
    accepted: Mapped[bool] = mapped_column(Boolean)
    
    # room_id: Mapped[int] = mapped_column(Integer)


class Message(Base):
    __tablename__ = "message"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    friendship_id: Mapped[int] = mapped_column(ForeignKey("friend.id"))
    # room_id: Mapped[int] = mapped_column(Integer)
    username: Mapped[str] = mapped_column(ForeignKey("user.username"))
    data = mapped_column(JSON)
    

# stateful counter used to generate the room id
class Counter():
    def __init__(self):
        self.counter = 0
    
    def get(self):
        self.counter += 1
        return self.counter

# Room class, used to keep track of which username is in which room
class Room():
    def __init__(self):
        self.counter = Counter()
        # dictionary that maps the username to the room id
        # for example self.dict["John"] -> gives you the room id of 
        # the room where John is in
        self.friends: Dict[int, int] = {}
        self.users: Dict[str, int] = {}

    def create_room(self, sender: str, receiver: str) -> int:
        room_id = self.counter.get()
        self.users[sender] = room_id
        self.users[receiver] = room_id
        return room_id

    def create_friend_room(self, friend_id) -> int:
        room_id = self.counter.get()
        self.friends[friend_id] = room_id
        return room_id
    
    def join_room(self,  sender: str, room_id: int) -> int:
        self.users[sender] = room_id

    def leave_room(self, user):
        if user not in self.users.keys():
            return
        del self.users[user]

    # gets the room id from a user
    def get_room_id(self, user: str):
        if user not in self.users.keys():
            return None
        return self.users[user]
    
    # gets the room id for a friendship
    def get_friend_room_id(self, friend: int):
        if friend not in self.friends.keys():
            return None
        return self.friends[friend]

    # gets the friendship id from a given room number
    def get_friend_from_room(self, room_id):
        for i in self.friends:
            if self.friends[i] == room_id:
                return i
        return None
    
