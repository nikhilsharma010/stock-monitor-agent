from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
import uuid

router = APIRouter()

@router.get("/", response_model=List[schemas.Thesis])
def get_theses(user_id: str, db: Session = Depends(get_db)):
    """Get all theses for a user"""
    theses = db.query(models.Thesis).filter(models.Thesis.user_id == user_id).all()
    return theses

@router.post("/", response_model=schemas.Thesis)
def create_thesis(thesis: schemas.ThesisCreate, user_id: str, db: Session = Depends(get_db)):
    """Create a new thesis"""
    db_thesis = models.Thesis(
        id=str(uuid.uuid4()),
        user_id=user_id,
        **thesis.dict()
    )
    db.add(db_thesis)
    db.commit()
    db.refresh(db_thesis)
    return db_thesis

@router.put("/{thesis_id}", response_model=schemas.Thesis)
def update_thesis(thesis_id: str, thesis: schemas.ThesisUpdate, user_id: str, db: Session = Depends(get_db)):
    """Update a thesis"""
    db_thesis = db.query(models.Thesis).filter(
        models.Thesis.id == thesis_id,
        models.Thesis.user_id == user_id
    ).first()
    
    if not db_thesis:
        raise HTTPException(status_code=404, detail="Thesis not found")
    
    for key, value in thesis.dict(exclude_unset=True).items():
        setattr(db_thesis, key, value)
    
    db.commit()
    db.refresh(db_thesis)
    return db_thesis

@router.delete("/{thesis_id}")
def delete_thesis(thesis_id: str, user_id: str, db: Session = Depends(get_db)):
    """Delete a thesis"""
    db_thesis = db.query(models.Thesis).filter(
        models.Thesis.id == thesis_id,
        models.Thesis.user_id == user_id
    ).first()
    
    if not db_thesis:
        raise HTTPException(status_code=404, detail="Thesis not found")
    
    db.delete(db_thesis)
    db.commit()
    return {"message": "Thesis deleted successfully"}
