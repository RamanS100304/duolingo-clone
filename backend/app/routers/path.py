from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import ChestOut, PathOut
from ..services import path, users
from .deps import current_user

router = APIRouter(tags=["path"])


@router.get("/path", response_model=PathOut)
def get_path(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return path.build_path(db, user)


@router.post("/units/{unit_id}/chest", response_model=ChestOut)
def open_chest(unit_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    gems = path.claim_chest(db, user, unit_id)
    db.commit()
    return {"gems_earned": gems, "user": users.user_state(db, user)}
