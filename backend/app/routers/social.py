from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import LeaderboardOut, ProfileOut, QuestsOut
from ..services import social
from .deps import current_user

router = APIRouter(tags=["social"])


@router.get("/leaderboard", response_model=LeaderboardOut)
def get_leaderboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return social.leaderboard(db, user)


@router.get("/profile", response_model=ProfileOut)
def get_profile(user: User = Depends(current_user), db: Session = Depends(get_db)):
    result = social.profile(db, user)
    db.commit()
    return result


@router.get("/quests", response_model=QuestsOut)
def get_quests(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return social.daily_quests(db, user)
