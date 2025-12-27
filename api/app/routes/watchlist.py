from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
import uuid

router = APIRouter()

@router.get("/", response_model=List[schemas.Watchlist])
def get_watchlist(user_id: str, db: Session = Depends(get_db)):
    """Get user's watchlist"""
    watchlist = db.query(models.Watchlist).filter(models.Watchlist.user_id == user_id).all()
    return watchlist

@router.post("/", response_model=schemas.Watchlist)
def add_to_watchlist(item: schemas.WatchlistCreate, user_id: str, db: Session = Depends(get_db)):
    """Add stock to watchlist"""
    # Check if already exists
    existing = db.query(models.Watchlist).filter(
        models.Watchlist.user_id == user_id,
        models.Watchlist.ticker == item.ticker
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Stock already in watchlist")
    
    db_item = models.Watchlist(
        id=str(uuid.uuid4()),
        user_id=user_id,
        **item.dict()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{ticker}")
def remove_from_watchlist(ticker: str, user_id: str, db: Session = Depends(get_db)):
    """Remove stock from watchlist"""
    db_item = db.query(models.Watchlist).filter(
        models.Watchlist.user_id == user_id,
        models.Watchlist.ticker == ticker
    ).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Stock not in watchlist")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Stock removed from watchlist"}

# Alerts
@router.get("/alerts", response_model=List[schemas.Alert])
def get_alerts(user_id: str, db: Session = Depends(get_db)):
    """Get user's alerts"""
    alerts = db.query(models.Alert).filter(models.Alert.user_id == user_id).all()
    return alerts

@router.post("/alerts", response_model=schemas.Alert)
def create_alert(alert: schemas.AlertCreate, user_id: str, db: Session = Depends(get_db)):
    """Create price alert"""
    db_alert = models.Alert(
        id=str(uuid.uuid4()),
        user_id=user_id,
        **alert.dict()
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.delete("/alerts/{alert_id}")
def delete_alert(alert_id: str, user_id: str, db: Session = Depends(get_db)):
    """Delete alert"""
    db_alert = db.query(models.Alert).filter(
        models.Alert.id == alert_id,
        models.Alert.user_id == user_id
    ).first()
    
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(db_alert)
    db.commit()
    return {"message": "Alert deleted successfully"}
