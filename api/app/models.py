from sqlalchemy import Column, String, DateTime, Decimal, Date, Boolean, Text, JSON
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
    target_amount = Column(Decimal, nullable=False)
    current_amount = Column(Decimal, default=0)
    target_date = Column(Date, nullable=False)
    monthly_contribution = Column(Decimal)
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
    performance = Column(Decimal)
    vs_market = Column(Decimal)
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
    target_price = Column(Decimal, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
