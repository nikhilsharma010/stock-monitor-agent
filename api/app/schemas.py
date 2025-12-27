from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

# Goal Schemas
class GoalBase(BaseModel):
    name: str
    category: Optional[str] = None
    target_amount: float
    current_amount: float = 0
    target_date: date
    monthly_contribution: Optional[float] = None

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    target_date: Optional[date] = None
    monthly_contribution: Optional[float] = None

class Goal(GoalBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Thesis Schemas
class StockAllocation(BaseModel):
    ticker: str
    allocation: float
    reason: str

class ThesisBase(BaseModel):
    name: str
    core_belief: Optional[str] = None
    catalysts: List[str] = []
    risks: List[str] = []
    stocks: List[StockAllocation] = []
    performance: Optional[float] = None
    vs_market: Optional[float] = None

class ThesisCreate(ThesisBase):
    pass

class ThesisUpdate(BaseModel):
    name: Optional[str] = None
    core_belief: Optional[str] = None
    catalysts: Optional[List[str]] = None
    risks: Optional[List[str]] = None
    stocks: Optional[List[StockAllocation]] = None
    performance: Optional[float] = None
    vs_market: Optional[float] = None

class Thesis(ThesisBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Watchlist Schemas
class WatchlistBase(BaseModel):
    ticker: str
    name: Optional[str] = None
    notes: Optional[str] = None

class WatchlistCreate(WatchlistBase):
    pass

class Watchlist(WatchlistBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# Alert Schemas
class AlertBase(BaseModel):
    ticker: str
    alert_type: str  # 'above' or 'below'
    target_price: float
    is_active: bool = True

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True
