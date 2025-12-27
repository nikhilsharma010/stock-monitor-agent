from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
import uuid

router = APIRouter()

@router.get("/", response_model=List[schemas.Goal])
def get_goals(user_id: str, db: Session = Depends(get_db)):
    """Get all goals for a user"""
    goals = db.query(models.Goal).filter(models.Goal.user_id == user_id).all()
    return goals

@router.post("/", response_model=schemas.Goal)
def create_goal(goal: schemas.GoalCreate, user_id: str, db: Session = Depends(get_db)):
    """Create a new goal"""
    db_goal = models.Goal(
        id=str(uuid.uuid4()),
        user_id=user_id,
        **goal.dict()
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

@router.put("/{goal_id}", response_model=schemas.Goal)
def update_goal(goal_id: str, goal: schemas.GoalUpdate, user_id: str, db: Session = Depends(get_db)):
    """Update a goal"""
    db_goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == user_id
    ).first()
    
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    for key, value in goal.dict(exclude_unset=True).items():
        setattr(db_goal, key, value)
    
    db.commit()
    db.refresh(db_goal)
    return db_goal

@router.delete("/{goal_id}")
def delete_goal(goal_id: str, user_id: str, db: Session = Depends(get_db)):
    """Delete a goal"""
    db_goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == user_id
    ).first()
    
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    db.delete(db_goal)
    db.commit()
    return {"message": "Goal deleted successfully"}
