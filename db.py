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

def accept_request(id):
    with Session(engine) as session:
        result = session.get(Friend, id)
        if result:
            result.accepted = True
            session.commit()
            return
        return f"Error: Couldn't find request {id}"
        

if __name__ == "__main__":
    with Session(engine) as session:
        session.add(Friend(id=1, frienda="alice", friendb="anne", accepted=True))
        session.add(Friend(id=2, frienda="alice", friendb="abby", accepted=True))
        session.add(Friend(id=3, frienda="alice", friendb="anya", accepted=True))
        session.add(Friend(id=4, frienda="bob", friendb="alice", accepted=False))
        session.add(Friend(id=5, frienda="brian", friendb="alice", accepted=False))
        session.add(Friend(id=6, frienda="alice", friendb="carol", accepted=False))
        session.add(Friend(id=7, frienda="alice", friendb="charles", accepted=False))
        session.commit()