from fastapi import Depends, Header
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..services.errors import not_found


def current_user(db: Session = Depends(get_db), x_user_id: int = Header(default=1)) -> User:
    """Auth is simplified (allowed by the brief): every request acts as the default learner (id 1).
    The X-User-Id header exists only so tests can act as another seeded user."""
    user = db.get(User, x_user_id)
    if not user:
        raise not_found("User")
    return user
