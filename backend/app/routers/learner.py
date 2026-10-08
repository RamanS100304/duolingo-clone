from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import SettingsIn, UserState
from ..services import hearts, users
from .deps import current_user

router = APIRouter(tags=["learner"])


@router.get("/me", response_model=UserState)
def get_me(user: User = Depends(current_user), db: Session = Depends(get_db)):
    state = users.user_state(db, user)
    db.commit()                      # persists lazy heart regeneration / streak expiry
    return state


@router.patch("/me", response_model=UserState)
def update_me(body: SettingsIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    users.update_settings(user, daily_goal_xp=body.daily_goal_xp, display_name=body.display_name,
                          timezone=body.timezone)
    db.commit()
    return users.user_state(db, user)


@router.post("/hearts/refill", response_model=UserState)
def refill_hearts(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Mock shop: spend gems to restore all hearts."""
    hearts.refill(user)
    db.commit()
    return users.user_state(db, user)
