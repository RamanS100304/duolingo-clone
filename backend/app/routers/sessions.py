from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import AnswerIn, AnswerOut, CompleteOut, PairIn, PairOut, SessionOut, SessionStartIn
from ..services import sessions, users
from .deps import current_user

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionOut, status_code=201)
def start_session(body: SessionStartIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Start a lesson / practice / timed / legendary run. The payload never contains answers."""
    session = sessions.start(db, user, body.kind, lesson_id=body.lesson_id, skill_id=body.skill_id,
                             unit_id=body.unit_id)
    db.commit()
    return sessions.session_out(db, session)


@router.post("/{session_id}/answers", response_model=AnswerOut)
def submit_answer(session_id: int, body: AnswerIn, user: User = Depends(current_user),
                  db: Session = Depends(get_db)):
    result = sessions.answer(db, user, session_id, body.exercise_id, body.answer)
    db.commit()
    return result


@router.post("/{session_id}/pairs", response_model=PairOut)
def submit_pair(session_id: int, body: PairIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    result = sessions.pair(db, user, session_id, body.exercise_id, body.left_id, body.right_id)
    db.commit()
    return result


@router.post("/{session_id}/complete", response_model=CompleteOut)
def complete_session(session_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    result = sessions.complete(db, user, session_id)
    db.commit()
    result["user"] = users.user_state(db, user)
    return result


@router.post("/{session_id}/abandon", status_code=204)
def abandon_session(session_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    sessions.abandon(db, user, session_id)
    db.commit()
    return Response(status_code=204)
