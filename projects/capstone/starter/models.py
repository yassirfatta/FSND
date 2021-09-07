from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json
import os

from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.schema import ForeignKey

database_name = "capstonedb"
database_path = "postgresql://{}/{}".format('localhost:5432', database_name)
db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()
    # add one demo row which is helping in POSTMAN test
    actor = Actor(
        name='Will Smith',
        gender='male'
    )
    actor.insert()

    movie = Movie(
    name = 'Men In Black',
    genre = 'Sci fi'
    )
    movie.insert()

'''
Actor
Have name and gender
'''
class Actor(db.Model):  
  __tablename__ = 'actors'

  id = Column(Integer, primary_key=True)
  name = Column(String)
  gender = Column(String)
  movie_id = Column(Integer, ForeignKey('movies.id'))

  def __init__(self, name, gender):
    self.name = name
    self.gender = gender

  def format(self):
    return {
      'id': self.id,
      'name': self.name,
      'gender': self.gender}

'''
Movie
Have name and genre
'''
class Movie(db.Model):  
  __tablename__ = 'movies'

  id = Column(Integer, primary_key=True)
  name = Column(String)
  genre = Column(String)
  actors = relationship('Actor', backref='movies', lazy=True)

  def __init__(self, name, genre):
    self.name = name
    self.genre = genre

  def format(self):
    return {
      'id': self.id,
      'name': self.name,
      'genre': self.genre}
