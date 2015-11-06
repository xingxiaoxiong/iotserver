import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Farm(Base):
    __tablename__ = 'farm'

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key = Column(String(16), unique=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    
class Greenhouse(Base):
    __tablename__ = 'greenhouse'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False)
    farm_id = Column(Integer, ForeignKey('farm.id'))
    farm = relationship(Farm)
    
class Node(Base):
    __tablename__ = 'node'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False)
    greenhouse_id = Column(Integer, ForeignKey('greenhouse.id'))
    greenhouse = relationship(Greenhouse)
    farm_id = Column(Integer, ForeignKey('farm.id'))
    farm = relationship(Farm)
    
    
class Temperature(Base):
    __tablename__ = 'temperature'

    id = Column(Integer, primary_key=True)
    value = Column(Float)
    datetime = Column(DateTime, default=datetime.datetime.utcnow)
    node_id = Column(Integer, ForeignKey('node.id'))
    node = relationship(Node)

class Humidity(Base):
    __tablename__ = 'humidity'

    id = Column(Integer, primary_key=True)
    value = Column(Float)
    datetime = Column(DateTime, default=datetime.datetime.utcnow)
    node_id = Column(Integer, ForeignKey('node.id'))
    node = relationship(Node)


engine = create_engine('mysql+pymysql://root:worldofiot@localhost')

engine.execute("CREATE DATABASE IF NOT EXISTS IoT")

engine.execute("USE IoT")

# engine.execute("CREATE TABLE IF NOT EXISTS User ( \
#     id int PRIMARY KEY AUTO_INCREMENT, \
#     api_key char(16) UNIQUE, \
#     name varchar(255) NOT NULL, \
#     email varchar(255) NOT NULL )"
# )

# engine.execute("CREATE TABLE IF NOT EXISTS Temperature ( \
#     id int PRIMARY KEY, \
#     value real, \
#     datetime datetime NOT NULL, \
#     user_id int, \
#     FOREIGN KEY (user_id) REFERENCES User(id) )"
# )

# engine = create_engine('mysql://root:worldofiot@localhost/sensorcloud')
# engine.execute("CREATE DATABASE SensorCloud") #create db
# engine.execute("USE SensorCloud") # select new db


Base.metadata.create_all(engine)
