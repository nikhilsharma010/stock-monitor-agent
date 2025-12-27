from sqlalchemy import Column, String, DateTime, Numeric, Date, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)  # Clerk user ID
    email = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    category = Column(String)
    target_amount = Column(Numeric(precision=15, scale=2), nullable=False)
    current_amount = Column(Numeric(precision=15, scale=2), default=0)
    target_date = Column(Date, nullable=False)
    monthly_contribution = Column(Numeric(precision=15, scale=2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Thesis(Base):
    __tablename__ = "theses"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    core_belief = Column(Text)
    catalysts = Column(JSON)  # Array of strings
    risks = Column(JSON)  # Array of strings
    stocks = Column(JSON)  # Array of {ticker, allocation, reason}
    performance = Column(Numeric(precision=10, scale=2))
    vs_market = Column(Numeric(precision=10, scale=2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Watchlist(Base):
    __tablename__ = "watchlist"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    ticker = Column(String, nullable=False)
    name = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    ticker = Column(String, nullable=False)
    alert_type = Column(String, nullable=False)  # 'above' or 'below'
    target_price = Column(Numeric(precision=15, scale=2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
