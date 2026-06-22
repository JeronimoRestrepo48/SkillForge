from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.instructor_profile import InstructorProfile
from app.models.user import User
from app.schemas.instructor import InstructorProfileOut, InstructorProfileUpdate
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/instructors", tags=["instructors"])

@router.get("/{user_id}/profile", response_model=InstructorProfileOut)
def get_instructor_profile(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(InstructorProfile).filter(InstructorProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Instructor profile not found")
    return profile

@router.put("/{user_id}/profile", response_model=InstructorProfileOut)
def update_instructor_profile(
    user_id: int,
    profile_data: InstructorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to modify this profile")

    # Ensure the user exists and is an instructor or admin
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role not in ["instructor", "admin"]:
        raise HTTPException(status_code=400, detail="User is not an instructor")

    profile = db.query(InstructorProfile).filter(InstructorProfile.user_id == user_id).first()
    if not profile:
        profile = InstructorProfile(user_id=user_id, **profile_data.dict(exclude_unset=True))
        db.add(profile)
    else:
        for key, value in profile_data.dict(exclude_unset=True).items():
            setattr(profile, key, value)
    
    db.commit()
    db.refresh(profile)
    return profile
