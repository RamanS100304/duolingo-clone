"""Study sessions: the server-side record of one run of the lesson player.

    start     deal the exercises (lesson / practice / timed / legendary), hearts checked up front
    answer    check one answer: only exercises of this session, hearts and limits enforced here
    pair      check one match-pairs pair (right tiles carry opaque tokens)
    complete  award XP / gems / progress only if the session was really finished
    abandon   the learner quit

The client never decides correctness, mistakes, XP or unlocks.
"""
import random
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import utcnow
from ..models import Exercise, Lesson, SessionAnswer, SessionExercise, Skill, StudySession, Unit, User, UserSkillProgress
from . import rules
from .achievements import check_achievements, new_badges_out
from .answers import check, pair_matches, serialize_exercise
from .clock import effective_today, register_activity, xp_today
from .errors import GameError, not_found
from .hearts import gain_heart, lose_heart, next_heart_in_sec, refresh_hearts, require_heart
from .path import is_complete, practice_pool, progress_map, skill_unlocked, unit_complete

SINGLE_TRY_KINDS = ("timed", "legendary")      # no second attempt, wrong answers are not repeated


# --------------------------------------------------------------------- start
def start(db: Session, user: User, kind: str, *, lesson_id: int | None = None,
          skill_id: int | None = None, unit_id: int | None = None) -> StudySession:
    lesson = None
    time_limit = max_mistakes = None
    if kind == "lesson":
        lesson = db.get(Lesson, lesson_id or 0)
        if not lesson:
            raise not_found("Lesson")
        if not skill_unlocked(db, user, lesson.skill):
            raise GameError(403, "locked", "This skill is locked")
        require_heart(user)
        skill_id = lesson.skill_id
        exercises = list(lesson.exercises)
    elif kind == "practice":
        if unit_id is not None:
            unit = db.get(Unit, unit_id)
            if not unit:
                raise not_found("Unit")
            if not unit_complete(unit, progress_map(db, user)):
                raise GameError(403, "locked", "Finish every skill of the unit to unlock its review")
        exercises = _sample(practice_pool(db, user, skill_id=skill_id, unit_id=unit_id), rules.PRACTICE_SIZE)
    elif kind == "timed":
        # Match-pairs is awkward under a clock, so timed mode skips it.
        exercises = _sample(practice_pool(db, user, exclude_types=("match_pairs",)), rules.TIMED_SIZE)
        time_limit = rules.TIMED_SECONDS
    elif kind == "legendary":
        skill = db.get(Skill, skill_id or 0)
        if not skill:
            raise not_found("Skill")
        if not is_complete(skill, progress_map(db, user)):
            raise GameError(403, "locked", "Finish every lesson of the skill to unlock its legendary challenge")
        exercises = _sample(practice_pool(db, user, skill_id=skill.id), rules.LEGENDARY_SIZE)
        max_mistakes = rules.LEGENDARY_MAX_MISTAKES
    else:
        raise GameError(400, "bad_kind", "Unknown session kind")
    if not exercises:
        raise GameError(400, "nothing_to_practice", "Complete a lesson first to unlock practice")

    # Only one session runs at a time: anything left open is abandoned.
    for old in db.scalars(select(StudySession).filter_by(user_id=user.id, status="active")):
        old.status, old.completed_at = "abandoned", utcnow()

    session = StudySession(user_id=user.id, kind=kind, status="active", lesson_id=lesson.id if lesson else None,
                           skill_id=skill_id, unit_id=unit_id, time_limit_sec=time_limit,
                           max_mistakes=max_mistakes, started_at=utcnow())
    session.items = [SessionExercise(exercise_id=e.id, position=i) for i, e in enumerate(exercises)]
    db.add(session)
    db.flush()
    return session


def _sample(pool: list[Exercise], size: int) -> list[Exercise]:
    return random.sample(pool, min(size, len(pool)))


def session_out(db: Session, session: StudySession) -> dict:
    title = None
    if session.lesson_id:
        lesson = db.get(Lesson, session.lesson_id)
        title = f"{lesson.skill.title} · Lesson {lesson.position}"
    elif session.skill_id:
        title = db.get(Skill, session.skill_id).title
    elif session.unit_id:
        title = f"{db.get(Unit, session.unit_id).title} review"
    return {"id": session.id, "kind": session.kind, "title": title, "lesson_id": session.lesson_id,
            "skill_id": session.skill_id, "unit_id": session.unit_id,
            "time_limit_sec": session.time_limit_sec, "max_mistakes": session.max_mistakes,
            "exercises": [serialize_exercise(it.exercise, session.id) for it in session.items]}


# ----------------------------------------------------------------- answering
def _active(db: Session, user: User, session_id: int) -> StudySession:
    session = db.get(StudySession, session_id)
    if not session or session.user_id != user.id:
        raise not_found("Session")
    if session.status == "failed":
        raise GameError(409, "challenge_failed", "This challenge has already failed")
    if session.status != "active":
        raise GameError(409, "session_closed", "This session is no longer active")
    return session


def _item(session: StudySession, exercise_id: int) -> SessionExercise:
    item = next((it for it in session.items if it.exercise_id == exercise_id), None)
    if not item:
        raise GameError(404, "not_in_session", "This exercise is not part of the session")
    if item.solved:
        raise GameError(409, "already_solved", "This exercise is already solved")
    if session.kind in SINGLE_TRY_KINDS and item.answered:
        raise GameError(409, "already_answered", "Only one try per question in this mode")
    return item


def _check_clock(session: StudySession) -> None:
    if session.time_limit_sec is None:
        return
    deadline = session.started_at + timedelta(seconds=session.time_limit_sec + rules.TIMED_GRACE_SEC)
    if utcnow() > deadline:
        raise GameError(409, "time_up", "Time is up")


def _register_mistake(session: StudySession, user: User, *, costs_heart: bool) -> None:
    session.mistakes += 1
    if costs_heart and session.kind == "lesson":
        lose_heart(user)
    if session.max_mistakes is not None and session.mistakes > session.max_mistakes:
        session.status, session.completed_at = "failed", utcnow()


def _state(session: StudySession, user: User) -> dict:
    refresh_hearts(user)
    return {"mistakes": session.mistakes, "correct_count": session.correct_count, "status": session.status,
            "remaining": sum(1 for it in session.items if not it.solved),
            "hearts": user.hearts, "next_heart_in_sec": next_heart_in_sec(user)}


def answer(db: Session, user: User, session_id: int, exercise_id: int, given: str) -> dict:
    session = _active(db, user, session_id)
    item = _item(session, exercise_id)
    _check_clock(session)
    if session.kind == "lesson":
        require_heart(user)
    ex = item.exercise
    correct, typo = check(ex, given)            # match-pairs sent here = skipped = wrong
    db.add(SessionAnswer(session_id=session.id, exercise_id=ex.id, answer=given[:500], is_correct=correct))
    item.answered = True
    if correct:
        item.solved = True
        session.correct_count += 1
    else:
        _register_mistake(session, user, costs_heart=True)
    return {"correct": correct, "typo": typo, "correct_answer": ex.primary_answer, **_state(session, user)}


def pair(db: Session, user: User, session_id: int, exercise_id: int, left_id: int, right_id: str) -> dict:
    session = _active(db, user, session_id)
    item = _item(session, exercise_id)
    ex = item.exercise
    if ex.type != "match_pairs":
        raise GameError(400, "not_match_pairs", "This exercise is not a match-pairs exercise")
    if left_id not in {o.id for o in ex.options}:
        raise GameError(400, "bad_tile", "Unknown tile")
    matched = set(db.scalars(select(SessionAnswer.answer).filter_by(
        session_id=session.id, exercise_id=ex.id, is_correct=True)))
    key = f"pair:{left_id}"
    if key in matched:
        raise GameError(409, "already_matched", "This pair is already matched")
    correct = pair_matches(session.id, left_id, right_id)
    db.add(SessionAnswer(session_id=session.id, exercise_id=ex.id, answer=key, is_correct=correct))
    if correct:
        matched.add(key)
        if len(matched) == len(ex.options):
            item.answered = item.solved = True
            session.correct_count += 1
    else:
        # Mismatched pairs count as mistakes but don't cost hearts (documented assumption).
        _register_mistake(session, user, costs_heart=False)
    return {"correct": correct, "exercise_solved": item.solved, **_state(session, user)}


# ----------------------------------------------------------------- finishing
def complete(db: Session, user: User, session_id: int) -> dict:
    session = _active(db, user, session_id)
    unsolved = [it for it in session.items if not it.solved]
    unanswered = [it for it in session.items if not it.answered]
    now = utcnow()

    if session.kind in ("lesson", "practice") and unsolved:
        raise GameError(409, "unfinished", "Answer every exercise correctly to finish")
    if session.kind == "legendary" and unanswered:
        raise GameError(409, "unfinished", "Answer every question to finish the challenge")
    if session.kind == "timed" and unanswered:
        ends = session.started_at + timedelta(seconds=session.time_limit_sec - 3)   # small clock slack
        if now < ends:
            raise GameError(409, "unfinished", "The clock is still running")

    xp, gems = 0, 0
    skill_completed = False
    if session.kind == "lesson":
        xp = rules.XP_LESSON + (rules.XP_LESSON_PERFECT_BONUS if session.mistakes == 0 else 0)
        gems = rules.GEMS_LESSON
        skill_completed = _advance_lesson(db, user, session)
    elif session.kind == "practice":
        xp = rules.XP_PRACTICE
        gain_heart(user)                                     # practising earns a heart back
    elif session.kind == "timed":
        xp = min(session.correct_count * rules.XP_PER_TIMED_ANSWER, rules.XP_TIMED_MAX)
        gems = rules.GEMS_TIMED_BONUS if session.correct_count >= 10 else 0
    else:
        xp, gems = rules.XP_LEGENDARY, rules.GEMS_LEGENDARY
        prog = db.scalar(select(UserSkillProgress).filter_by(user_id=user.id, skill_id=session.skill_id))
        prog.legendary = True

    streak_before = user.streak
    xp_before = xp_today(db, user)
    increased = register_activity(user) if xp > 0 else False   # an empty timed run earns no streak credit

    session.status, session.completed_at = "completed", now
    session.activity_date = effective_today(user)
    session.xp_earned, session.gems_earned = xp, gems
    session.duration_sec = max(1, int((now - session.started_at).total_seconds()))
    user.total_xp += xp
    user.gems += gems
    badges = check_achievements(db, user)

    attempts = session.correct_count + session.mistakes
    return {
        "kind": session.kind, "xp_earned": xp, "gems_earned": gems,
        "correct_count": session.correct_count, "mistakes": session.mistakes,
        "accuracy": round(100 * session.correct_count / attempts) if attempts else 100,
        "duration_sec": session.duration_sec, "perfect": session.mistakes == 0,
        "skill_completed": skill_completed,
        "streak": {"before": streak_before, "after": user.streak, "increased": increased},
        "daily_goal_reached": xp > 0 and xp_before < user.daily_goal_xp <= xp_before + xp,
        "new_achievements": new_badges_out(badges),
    }


def _advance_lesson(db: Session, user: User, session: StudySession) -> bool:
    """Only the *next* lesson of a skill advances progress; replays just give XP."""
    lesson = db.get(Lesson, session.lesson_id)
    prog = db.scalar(select(UserSkillProgress).filter_by(user_id=user.id, skill_id=lesson.skill_id))
    if prog is None:
        prog = UserSkillProgress(user_id=user.id, skill_id=lesson.skill_id, lessons_completed=0)
        db.add(prog)
    newly_done = lesson.position == prog.lessons_completed + 1
    if newly_done:
        prog.lessons_completed += 1
    return newly_done and prog.lessons_completed >= len(lesson.skill.lessons)


def abandon(db: Session, user: User, session_id: int) -> None:
    session = db.get(StudySession, session_id)
    if not session or session.user_id != user.id:
        raise not_found("Session")
    if session.status == "active":
        session.status, session.completed_at = "abandoned", utcnow()
