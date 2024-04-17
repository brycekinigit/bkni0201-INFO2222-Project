'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import *
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from models import *

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
def insert_user(username: str, password: str):
    with Session(engine) as session:
        user = User(username=username, password=password)
        session.add(user)
        session.commit()

# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)



def get_friends(username):
    with Session(engine) as session:
        resulta = session.execute(select(Friend).where(Friend.frienda == username)).all()
        resultb = session.execute(select(Friend).where(Friend.friendb == username)).all()
        return [row[0] for row in resulta] + [row[0] for row in resultb]

def accept_request(id, username):
    with Session(engine) as session:
        result = session.get(Friend, id)
        result.accepted = True
        session.commit()
        

if __name__ == "__main__":
    insert_user("alice", "alice123")
    insert_user("bob", "bob123")
    insert_user("carol", "carol123")
    with Session(engine) as session:
        session.add(Friend(id=1, frienda="alice", friendb="bob", accepted=True))
        session.add(Friend(id=2, frienda="alice", friendb="anne", accepted=True))
        session.add(Friend(id=3, frienda="bob", friendb="brian", accepted=True))
        session.add(Friend(id=4, frienda="bob", friendb="carol", accepted=False))
        session.add(Friend(id=5, frienda="carol", friendb="charles", accepted=True))
        session.add(Friend(id=6, frienda="carol", friendb="alice", accepted=True))
        
        session.commit()