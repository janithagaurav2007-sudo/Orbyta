from sqlalchemy import Column, Integer, Float, String, DateTime, Text, UniqueConstraint
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, default="")
    age = Column(Integer, nullable=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    amie_name = Column(String, default="Amie")
    amie_avatar = Column(String, default="bear")
    theme = Column(String, default="light")

class ScreeningResult(Base):
    __tablename__ = "screening_results"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    probability = Column(Float)
    level = Column(String)
    factors = Column(Text, default="[]")
    inputs = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

class CycleEntry(Base):
    __tablename__ = "cycle_entries"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    start_date = Column(String)
    end_date = Column(String)
    flow = Column(String, default="Medium")
    cramps = Column(Integer, default=0)
    mood = Column(String, default="Okay")
    energy = Column(Integer, default=3)

class SymptomEntry(Base):
    __tablename__ = "symptom_entries"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    symptom = Column(String)
    severity = Column(Integer, default=2)
    date = Column(String)

class Checkin(Base):
    __tablename__ = "checkins"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    mood = Column(Integer, default=3)
    energy = Column(Integer, default=3)
    stress = Column(Integer, default=3)
    sleep = Column(Float, default=7)
    created_at = Column(DateTime, default=datetime.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    message = Column(Text)
    reply = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
