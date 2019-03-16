import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class GmailUser(Base):
    __tablename__ = 'gmailuser'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(220), nullable=False)


class GameFranchiseName(Base):
    __tablename__ = 'gamefranchisename'
    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    user_id = Column(Integer, ForeignKey('gmailuser.id'))
    user = relationship(GmailUser, backref="gamefranchisename")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self.name,
            'id': self.id
        }


class GameTitle(Base):
    __tablename__ = 'gamename1'
    id = Column(Integer, primary_key=True)
    gamename = Column(String(350), nullable=False)
    launchyear = Column(String(150))
    rating = Column(String(150))
    gametype = Column(String(150))
    price = Column(String(10))
    date = Column(DateTime, nullable=False)
    gamefranchisenameid = Column(Integer, ForeignKey('gamefranchisename.id'))
    gamefranchisename = relationship(
        GameFranchiseName, backref=backref('gamename', cascade='all, delete'))
    gmailuser_id = Column(Integer, ForeignKey('gmailuser.id'))
    gmailuser = relationship(GmailUser, backref="gamename1")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'gamename': self. gamename,
            'launchyear': self. launchyear,
            'rating': self. rating,
            'price': self. price,
            'gametype': self. gametype,
            'date': self. date,
            'id': self. id
        }

engin = create_engine('sqlite:///games.db')
Base.metadata.create_all(engin)
