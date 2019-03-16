from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from Data_Setup import *

engine = create_engine('sqlite:///games.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Delete GameFranchiseName if exisitng.
session.query(GameFranchiseName).delete()
# Delete GameTitle if exisitng.
session.query(GameTitle).delete()
# Delete GmailUser if exisitng.
session.query(GmailUser).delete()

# Create sample users data
User1 = GmailUser(name="Raghuveer Pachipulusu",
                  email="ptnbvr@gmail.com",)
session.add(User1)
session.commit()
print ("Successfully Add First User")
# Create sample GameFranchise
Franchise1 = GameFranchiseName(name="Assassins Creed",
                               user_id=1)
session.add(Franchise1)
session.commit()

Franchise2 = GameFranchiseName(name="Grand Theft Auto",
                               user_id=1)
session.add(Franchise2)
session.commit

Franchise3 = GameFranchiseName(name="Far Cry",
                               user_id=1)
session.add(Franchise3)
session.commit()

Franchise4 = GameFranchiseName(name="Need For Speed",
                               user_id=1)
session.add(Franchise4)
session.commit()

Franchise5 = GameFranchiseName(name="Fallout",
                               user_id=1)
session.add(Franchise5)
session.commit()

Franchise6 = GameFranchiseName(name="Call Of Duty",
                               user_id=1)
session.add(Franchise6)
session.commit()

# Populare a bykes with models for testing
# Using different users for bykes names year also
Game1 = GameTitle(gamename="Assassins Creed Odessy",
                  launchyear="2018",
                  rating="9.2",
                  price="650/-",
                  gametype="action role-play",
                  date=datetime.datetime.now(),
                  gamefranchisenameid=1,
                  gmailuser_id=1)
session.add(Game1)
session.commit()

Game2 = GameTitle(gamename="Grand Theft Auto V",
                  launchyear="2013",
                  rating="10",
                  price="2,089/-",
                  gametype=" action-adventure",
                  date=datetime.datetime.now(),
                  gamefranchisenameid=2,
                  gmailuser_id=1)
session.add(Game2)
session.commit()

Game3 = GameTitle(gamename="Far Cry 5",
                  launchyear="2018",
                  rating="8.9",
                  price="2,500/-",
                  gametype="first-person shooter",
                  date=datetime.datetime.now(),
                  gamefranchisenameid=3,
                  gmailuser_id=1)
session.add(Game3)
session.commit()

Game4 = GameTitle(gamename="Need for Speed: Most Wanted",
                  launchyear="2012",
                  rating="9",
                  price="950/-",
                  gametype="car racing ",
                  date=datetime.datetime.now(),
                  gamefranchisenameid=4,
                  gmailuser_id=1)
session.add(Game4)
session.commit()

Game5 = GameTitle(gamename="Fallout 4 ",
                  launchyear="2015",
                  rating="9.5",
                  price="1,065/-",
                  gametype="action role-play",
                  date=datetime.datetime.now(),
                  gamefranchisenameid=5,
                  gmailuser_id=1)
session.add(Game5)
session.commit()

Game6 = GameTitle(gamename="Call of Duty: Black Ops 4",
                  launchyear="2018",
                  rating="8.5",
                  price="730/-",
                  gametype=" first-person shooter",
                  date=datetime.datetime.now(),
                  gamefranchisenameid=6,
                  gmailuser_id=1)
session.add(Game6)
session.commit()

print("Your games database has been inserted!")
