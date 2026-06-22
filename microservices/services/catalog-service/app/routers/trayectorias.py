from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.trayectoria import Trayectoria, TrayectoriaCurso
from app.models.course import Course
from app.schemas.catalog import (
    TrayectoriaOut, 
    TrayectoriaDetailOut, 
    TrayectoriaCreate, 
    TrayectoriaAddCurso
)
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/trayectorias", tags=["trayectorias"])

@router.get("", response_model=List[TrayectoriaOut])
def list_trayectorias(db: Session = Depends(get_db)):
    return db.query(Trayectoria).all()

@router.get("/{id}", response_model=TrayectoriaDetailOut)
def get_trayectoria(id: int, db: Session = Depends(get_db)):
    t = db.query(Trayectoria).filter(Trayectoria.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Trayectoria not found")
    return t

@router.post("", response_model=TrayectoriaOut, status_code=status.HTTP_201_CREATED)
def create_trayectoria(
    trayectoria_data: TrayectoriaCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    t = Trayectoria(**trayectoria_data.dict())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t

@router.put("/{id}", response_model=TrayectoriaOut)
def update_trayectoria(
    id: int,
    trayectoria_data: TrayectoriaCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    t = db.query(Trayectoria).filter(Trayectoria.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Trayectoria not found")
        
    for key, value in trayectoria_data.dict().items():
        setattr(t, key, value)
        
    db.commit()
    db.refresh(t)
    return t

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trayectoria(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    t = db.query(Trayectoria).filter(Trayectoria.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Trayectoria not found")
        
    db.delete(t)
    db.commit()
    return None

@router.post("/{id}/cursos", response_model=TrayectoriaDetailOut)
def add_curso_to_trayectoria(
    id: int,
    curso_data: TrayectoriaAddCurso,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    t = db.query(Trayectoria).filter(Trayectoria.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Trayectoria not found")
        
    c = db.query(Course).filter(Course.id == curso_data.course_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
        
    existing = db.query(TrayectoriaCurso).filter(
        TrayectoriaCurso.trayectoria_id == id,
        TrayectoriaCurso.course_id == curso_data.course_id
    ).first()
    
    if existing:
        existing.sort_order = curso_data.sort_order
    else:
        tc = TrayectoriaCurso(
            trayectoria_id=id,
            course_id=curso_data.course_id,
            sort_order=curso_data.sort_order
        )
        db.add(tc)
        
    db.commit()
    db.refresh(t)
    return t

@router.delete("/{id}/cursos/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_curso_from_trayectoria(
    id: int,
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    tc = db.query(TrayectoriaCurso).filter(
        TrayectoriaCurso.trayectoria_id == id,
        TrayectoriaCurso.course_id == course_id
    ).first()
    
    if not tc:
        raise HTTPException(status_code=404, detail="Course not found in Trayectoria")
        
    db.delete(tc)
    db.commit()
    return None
