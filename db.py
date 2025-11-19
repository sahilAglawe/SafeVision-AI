import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Database URL can be set via the DATABASE_URL environment variable.
# Default to a local SQLite file 'incidents.db' for simplicity and portability.
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///incidents.db')

engine_kwargs = {}
if DATABASE_URL.startswith('sqlite'):
    # SQLite requires this flag for multi-threaded access in the app
    engine_kwargs['connect_args'] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()


class Incident(Base):
    __tablename__ = 'incidents'
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    label = Column(String(255))
    severity = Column(String(50))
    zone = Column(String(100))
    description = Column(Text)
    confidence = Column(Float)


def init_db():
    """Create database tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Return a new SQLAlchemy session (scoped). Call `remove()` when done if needed."""
    return SessionLocal()
