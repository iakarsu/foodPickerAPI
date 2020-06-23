from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.types import DateTime
from dotenv import load_dotenv
import os

load_dotenv(verbose=True)

Base = declarative_base()
db_string = os.getenv("DB_STRING")
engine = create_engine(db_string)
Session = sessionmaker(bind=engine)
session = Session()

class City(Base):
    __tablename__ = 'city'
    
    id = Column(Integer, primary_key=True)

    name = Column(String(200), unique= True)
    link = Column(String(200))
    population = Column(BigInteger, default = 0)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)

    district = relationship('District', backref='city', lazy=True)

    def __repr__(self):
        return f"City('{self.name}', '{self.link}', '{self.population}')"

class District(Base):
    __tablename__ = 'district'
    
    id = Column(Integer, primary_key=True)

    name = Column(String(200), nullable=False)
    link = Column(String(200), unique=True, nullable=False)
    district_y_id = Column(String(200), unique=True, nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)

    #relationships
    city_id = Column(Integer, ForeignKey('city.id'), nullable=False)
    restaurant = relationship('Restaurant', backref='district', lazy=True)

    def __repr__(self):
        return f"District('{self.name}', '{self.id}')"

class Restaurant(Base):
    __tablename__ = 'restaurant'
    
    id = Column(Integer, primary_key=True)

    name = Column(String(200), unique=False, nullable=False)
    link = Column(String(200), unique=True, nullable=False)
    speed = Column(String(10), nullable=True)
    service = Column(String(10), nullable=False)
    taste = Column(String(10), nullable=False)
    average = Column(String(10), nullable=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)

    #relationships
    district_id = Column(Integer, ForeignKey('district.id'), nullable=False)
    comment = relationship('Comment', backref='restaurant', lazy=True)

    def __repr__(self):
        return f"Restaurant('{self.name}', '{self.district_id}')"

class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key= True)

    speed = Column(String(10), nullable=True)
    service = Column(String(10), nullable=False)
    taste = Column(String(10), nullable=False)
    text = Column(String(500), nullable=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)

    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)

    def __repr__(self):
        return f"Comment('{self.id}', '{self.restaurant_id}')"

class Pending_Restaurants(Base):
    __tablename__ = 'pending_restaurant'
    
    id = Column(Integer, primary_key=True)

    name = Column(String(200), unique=True, nullable=False)
    link = Column(String(200), unique=True, nullable=False)
    speed = Column(Integer, nullable=True)
    service = Column(Integer, nullable=False)
    taste = Column(Integer, nullable=False)
    average = Column(Integer, nullable=False)
    status = Column(Boolean, default = 1)
    district_id = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Pending('{self.name}', '{self.status}')"

class Pending_Comments(Base):
    __tablename__ = 'pending_comments'
    id = Column(Integer, primary_key=True)

    restaurant_id = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
Base.metadata.bind = engine
def db_create():
    Base.metadata.create_all()
