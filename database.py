from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Metric(Base):
    __tablename__ = 'metrics'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    cpu_usage = Column(Float)  # %
    ram_usage = Column(Float)  # %
    request_latency = Column(Float) # мс (симуляция)
    source = Column(String) # "System" или ID алгоритма

class Algorithm(Base):
    __tablename__ = 'algorithms'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    version = Column(String)
    status = Column(String) # Active, Testing, Deprecated
    description = Column(String)

class Recommendation(Base):
    __tablename__ = 'recommendations'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    type = Column(String) # Scaling, AlgorithmSwitch
    message = Column(String)
    status = Column(String) # Pending, Applied, Rejected

# Инициализация БД
engine = create_engine('sqlite:///system.db', connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def get_session():
    return session