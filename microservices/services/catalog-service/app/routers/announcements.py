from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.announcement import Announcement
from app.schemas.catalog import AnnouncementCreate, AnnouncementOut
from app.dependencies.auth import get_current_user, UserPayload

router = APIRouter()


@router.get("/announcements", response_model=List[AnnouncementOut])
def list_announcements(db: Session = Depends(get_db)):
    """Público: retorna anuncios activos ordenados por fecha de creación DESC."""
    return (
        db.query(Announcement)
        .filter(Announcement.activo == True)
        .order_by(Announcement.created_at.desc())
        .all()
    )


@router.post("/announcements", response_model=AnnouncementOut, status_code=status.HTTP_201_CREATED)
def create_announcement(
    payload: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user),
):
    if current_user.role not in ("admin", "administrador"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores pueden crear anuncios.")
    announcement = Announcement(**payload.model_dump())
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement


@router.put("/announcements/{announcement_id}", response_model=AnnouncementOut)
def update_announcement(
    announcement_id: int,
    payload: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user),
):
    if current_user.role not in ("admin", "administrador"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores pueden editar anuncios.")
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anuncio no encontrado.")
    for key, value in payload.model_dump().items():
        setattr(announcement, key, value)
    db.commit()
    db.refresh(announcement)
    return announcement


@router.delete("/announcements/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user),
):
    if current_user.role not in ("admin", "administrador"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores pueden eliminar anuncios.")
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anuncio no encontrado.")
    db.delete(announcement)
    db.commit()
