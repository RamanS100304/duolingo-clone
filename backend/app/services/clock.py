"""The learner's 'today', streak rules and daily-XP aggregates."""
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import DEFAULT_TIMEZONE
from ..models import StudySession, User


def valid_timezone(name: str) -> bool:
    try:
        ZoneInfo(name)
        return True
    except (ZoneInfoNotFoundError, ValueError):
        return False


def effective_today(user: User) -> date:
    """'Today' in the learner's own time zone; day_offset simulates days passing."""
    tz = ZoneInfo(user.timezone if valid_timezone(user.timezone or "") else DEFAULT_TIMEZONE)
    return datetime.now(timezone.utc).astimezone(tz).date() + timedelta(days=user.day_offset)


def refresh_streak(user: User) -> None:
    """A streak survives only if the learner was active today or yesterday."""
    if user.last_active_date and user.last_active_date < effective_today(user) - timedelta(days=1):
        user.streak = 0


def register_activity(user: User) -> bool:
    """Count today towards the streak. Returns True if this is the first activity of the day."""
    refresh_streak(user)
    today = effective_today(user)
    if user.last_active_date == today:
        return False
    user.streak = user.streak + 1 if user.last_active_date == today - timedelta(days=1) else 1
    user.last_active_date = today
    user.longest_streak = max(user.longest_streak, user.streak)
    return True


def completed_sessions():
    return select(StudySession).where(StudySession.status == "completed")


def daily_xp_by_date(db: Session, user: User) -> dict[date, int]:
    rows = db.execute(
        select(StudySession.activity_date, func.sum(StudySession.xp_earned))
        .where(StudySession.user_id == user.id, StudySession.status == "completed")
        .group_by(StudySession.activity_date)).all()
    return {d: int(x or 0) for d, x in rows if d is not None}


def xp_today(db: Session, user: User) -> int:
    return daily_xp_by_date(db, user).get(effective_today(user), 0)


def week_activity(db: Session, user: User) -> list[dict]:
    today, by_date = effective_today(user), daily_xp_by_date(db, user)
    days = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        days.append({"date": d.isoformat(), "label": d.strftime("%a"), "xp": by_date.get(d, 0),
                     "active": by_date.get(d, 0) > 0, "is_today": i == 0})
    return days
