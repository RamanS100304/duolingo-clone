"""Unlock rules, the learning path and practice pools."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import ChestClaim, Exercise, Skill, Unit, User, UserSkillProgress
from .errors import GameError, not_found
from .rules import CHEST_AFTER_SKILL, CHEST_GEMS


def ordered_skills(db: Session) -> list[Skill]:
    return list(db.scalars(select(Skill).join(Unit).order_by(Unit.position, Skill.position)))


def progress_map(db: Session, user: User) -> dict[int, UserSkillProgress]:
    return {p.skill_id: p for p in db.scalars(
        select(UserSkillProgress).where(UserSkillProgress.user_id == user.id))}


def is_complete(skill: Skill, prog: dict[int, UserSkillProgress]) -> bool:
    p = prog.get(skill.id)
    return bool(p and p.lessons_completed >= len(skill.lessons))


def skill_unlocked(db: Session, user: User, skill: Skill) -> bool:
    """A skill is open once every skill before it (across units) is complete."""
    prog = progress_map(db, user)
    for s in ordered_skills(db):
        if s.id == skill.id:
            return True
        if not is_complete(s, prog):
            return False
    return False


def unit_complete(unit: Unit, prog: dict[int, UserSkillProgress]) -> bool:
    return all(is_complete(s, prog) for s in unit.skills)


def build_path(db: Session, user: User) -> dict:
    """Units with their nodes in path order: skills, a treasure chest mid-unit and a trophy at the end."""
    prog = progress_map(db, user)
    claimed = set(db.scalars(select(ChestClaim.unit_id).where(ChestClaim.user_id == user.id)))
    prev_done, current_marked = True, False
    units_out = []
    for unit in db.scalars(select(Unit).order_by(Unit.position)):
        nodes = []
        for i, s in enumerate(unit.skills, start=1):
            p = prog.get(s.id)
            done_count = min(p.lessons_completed if p else 0, len(s.lessons))
            completed = done_count >= len(s.lessons)
            state = "completed" if completed else ("available" if prev_done else "locked")
            is_current = state == "available" and not current_marked
            current_marked = current_marked or is_current
            nodes.append({
                "type": "skill", "id": s.id, "title": s.title, "icon": s.icon, "state": state,
                "lessons_total": len(s.lessons), "lessons_completed": done_count,
                "legendary": bool(p and p.legendary), "is_current": is_current,
                "next_lesson_id": s.lessons[done_count].id if state == "available" else None,
            })
            prev_done = completed
            if i == CHEST_AFTER_SKILL and len(unit.skills) > CHEST_AFTER_SKILL:
                chest_state = "claimed" if unit.id in claimed else ("available" if completed else "locked")
                nodes.append({"type": "chest", "id": unit.id, "title": "Treasure chest", "state": chest_state,
                              "gems": CHEST_GEMS})
        trophy_state = "completed" if unit_complete(unit, prog) else "locked"
        nodes.append({"type": "trophy", "id": unit.id, "title": f"{unit.title} review", "state": trophy_state})
        units_out.append({"id": unit.id, "title": unit.title, "description": unit.description,
                          "color": unit.color, "position": unit.position, "nodes": nodes})
    return {"units": units_out}


def claim_chest(db: Session, user: User, unit_id: int) -> int:
    unit = db.get(Unit, unit_id)
    if not unit:
        raise not_found("Unit")
    if len(unit.skills) <= CHEST_AFTER_SKILL:
        raise not_found("Chest")
    if not is_complete(unit.skills[CHEST_AFTER_SKILL - 1], progress_map(db, user)):
        raise GameError(403, "locked", "Finish the skill before the chest to open it")
    if db.scalar(select(ChestClaim.id).filter_by(user_id=user.id, unit_id=unit_id)):
        raise GameError(409, "already_claimed", "This chest is already open")
    db.add(ChestClaim(user_id=user.id, unit_id=unit_id, gems=CHEST_GEMS))
    user.gems += CHEST_GEMS
    return CHEST_GEMS


def practice_pool(db: Session, user: User, *, skill_id: int | None = None,
                  unit_id: int | None = None, exclude_types: tuple[str, ...] = ()) -> list[Exercise]:
    """Exercises from lessons the learner has already completed (optionally one skill or unit)."""
    prog = progress_map(db, user)
    pool: list[Exercise] = []
    for s in ordered_skills(db):
        p = prog.get(s.id)
        if not p or p.lessons_completed == 0:
            continue
        if (skill_id and s.id != skill_id) or (unit_id and s.unit_id != unit_id):
            continue
        for lesson in s.lessons[:p.lessons_completed]:
            pool.extend(e for e in lesson.exercises if e.type not in exclude_types)
    return pool
