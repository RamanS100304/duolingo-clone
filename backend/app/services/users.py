"""The learner snapshot returned to the client, settings and progress reset."""
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..config import ENABLE_DEV_TOOLS
from ..models import ChestClaim, Course, League, StudySession, User, UserAchievement, UserSkillProgress
from .clock import effective_today, refresh_streak, valid_timezone, week_activity, xp_today
from .errors import GameError
from .hearts import next_heart_in_sec, refresh_hearts
from .rules import MAX_HEARTS, REFILL_COST_GEMS


def user_state(db: Session, user: User) -> dict:
    refresh_hearts(user)
    refresh_streak(user)
    course = db.scalar(select(Course).order_by(Course.id))
    return {
        "id": user.id, "username": user.username, "display_name": user.display_name,
        "avatar_color": user.avatar_color, "total_xp": user.total_xp, "gems": user.gems,
        "hearts": user.hearts, "max_hearts": MAX_HEARTS, "next_heart_in_sec": next_heart_in_sec(user),
        "streak": user.streak, "longest_streak": user.longest_streak,
        "streak_active_today": user.last_active_date == effective_today(user),
        "daily_goal_xp": user.daily_goal_xp, "daily_xp": xp_today(db, user),
        "week": week_activity(db, user), "day_offset": user.day_offset, "timezone": user.timezone,
        "refill_cost": REFILL_COST_GEMS, "league": user.league.name if user.league else None,
        "dev_tools": ENABLE_DEV_TOOLS,
        "course": {"title": course.title, "from_language": course.from_language,
                   "to_language": course.to_language} if course else None,
    }


def update_settings(user: User, *, daily_goal_xp: int | None, display_name: str | None,
                    timezone: str | None) -> None:
    if daily_goal_xp is not None:
        user.daily_goal_xp = daily_goal_xp
    if display_name is not None:
        if not display_name.strip():
            raise GameError(422, "bad_name", "Display name can't be empty")
        user.display_name = display_name.strip()
    if timezone is not None:
        if not valid_timezone(timezone):
            raise GameError(422, "bad_timezone", "Unknown time zone")
        user.timezone = timezone


def wipe_progress(db: Session, user: User) -> None:
    """Delete all learning history of this learner and reset the counters (account is kept)."""
    for model in (StudySession, UserSkillProgress, UserAchievement, ChestClaim):
        db.execute(delete(model).where(model.user_id == user.id))
    user.total_xp, user.gems, user.hearts, user.streak, user.longest_streak = 0, 500, MAX_HEARTS, 0, 0
    user.last_active_date, user.day_offset = None, 0
    user.league_id = db.scalar(select(League.id).where(League.tier == 1))
