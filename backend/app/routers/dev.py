"""Testing aids for reviewers. Only mounted when ENABLE_DEV_TOOLS is true."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import DayIn, ResetIn, UserState
from ..seed import refresh_rivals, restore_demo_history
from ..services import clock, users
from .deps import current_user

router = APIRouter(prefix="/dev", tags=["dev tools"])


@router.post("/advance-day", response_model=UserState)
def advance_day(body: DayIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Pretend N days have passed so streak logic can be exercised."""
    user.day_offset += body.days
    clock.refresh_streak(user)
    db.commit()
    return users.user_state(db, user)


@router.post("/reset", response_model=UserState)
def reset_progress(body: ResetIn = ResetIn(), user: User = Depends(current_user), db: Session = Depends(get_db)):
    """mode=demo restores the sample learner (dated relative to today); mode=empty starts from zero."""
    users.wipe_progress(db, user)
    db.flush()
    if body.mode == "demo":
        restore_demo_history(db, user)
        refresh_rivals(db)
    db.commit()
    return users.user_state(db, user)
