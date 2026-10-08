"""Hearts: lost on mistakes in lessons, regenerated lazily over time (no background job)."""
from datetime import timedelta

from ..database import utcnow
from ..models import User
from .errors import GameError
from .rules import HEART_REGEN_SEC, MAX_HEARTS, REFILL_COST_GEMS


def refresh_hearts(user: User) -> None:
    """Apply time-based regeneration whenever hearts are read."""
    now = utcnow()
    if user.hearts >= MAX_HEARTS:
        user.hearts, user.hearts_updated_at = MAX_HEARTS, now
        return
    gained = int((now - user.hearts_updated_at).total_seconds() // HEART_REGEN_SEC)
    if gained > 0:
        user.hearts = min(MAX_HEARTS, user.hearts + gained)
        user.hearts_updated_at = now if user.hearts >= MAX_HEARTS else (
            user.hearts_updated_at + timedelta(seconds=gained * HEART_REGEN_SEC))


def lose_heart(user: User) -> None:
    refresh_hearts(user)
    if user.hearts <= 0:
        return
    if user.hearts == MAX_HEARTS:          # the regeneration timer starts at the first lost heart
        user.hearts_updated_at = utcnow()
    user.hearts -= 1


def gain_heart(user: User) -> None:
    refresh_hearts(user)
    user.hearts = min(MAX_HEARTS, user.hearts + 1)


def next_heart_in_sec(user: User) -> int:
    if user.hearts >= MAX_HEARTS:
        return 0
    elapsed = (utcnow() - user.hearts_updated_at).total_seconds()
    return max(0, int(HEART_REGEN_SEC - elapsed))


def require_heart(user: User) -> None:
    refresh_hearts(user)
    if user.hearts <= 0:
        raise GameError(403, "out_of_hearts", "You're out of hearts. Practice or refill to continue.")


def refill(user: User) -> None:
    """Mock shop: spend gems to restore all hearts."""
    refresh_hearts(user)
    if user.hearts >= MAX_HEARTS:
        raise GameError(400, "hearts_full", "Hearts are already full")
    if user.gems < REFILL_COST_GEMS:
        raise GameError(400, "not_enough_gems", "Not enough gems")
    user.gems -= REFILL_COST_GEMS
    user.hearts, user.hearts_updated_at = MAX_HEARTS, utcnow()
