"""Seeds the course, leagues, achievements, a demo learner with some progress and leaderboard rivals.

Idempotent: does nothing if a course already exists.  Run manually with:  python -m app.seed
"""
import random
import re
from datetime import date, datetime, time, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from . import content
from .database import SessionLocal
from .models import (Achievement, Course, Exercise, ExerciseAnswer, ExerciseOption, League, Lesson, Skill,
                     StudySession, Unit, User, UserSkillProgress)
from .services import rules
from .services.achievements import check_achievements
from .services.clock import effective_today
from .services.path import ordered_skills

TOKEN = re.compile(r"[A-Za-z]+")


# ------------------------------------------------------------------ content
def _answers(primary: str, alternatives: list[str] | tuple = ()) -> list[ExerciseAnswer]:
    out = [ExerciseAnswer(text=primary, is_primary=True)]
    out += [ExerciseAnswer(text=a, is_primary=False) for a in dict.fromkeys(alternatives) if a != primary]
    return out


def _options(texts: list[str], correct: str | None = None) -> list[ExerciseOption]:
    return [ExerciseOption(position=i, text=t, is_correct=(t == correct)) for i, t in enumerate(texts)]


def build_lesson_exercises(skill_def: dict, li: int) -> list[Exercise]:
    """Expand a skill's vocabulary + sentences into 8 varied exercises for lesson #li."""
    rng = random.Random(f"{skill_def['title']}-{li}")
    words, sentences = skill_def["words"], skill_def["sentences"]
    rot = words[li * 3 % len(words):] + words[:li * 3 % len(words)]
    sa, sb = sentences[(2 * li) % len(sentences)], sentences[(2 * li + 1) % len(sentences)]
    all_tokens = {t for s in sentences for t in TOKEN.findall(s[1])}

    def mcq(word, to_hindi: bool) -> Exercise:
        en, hi = word
        wrong = rng.sample([w for w in words if w != word], 3)
        if to_hindi:   # English word shown, pick the Hindi meaning
            opts, ans = [hi] + [w[1] for w in wrong], hi
            ex = Exercise(type="multiple_choice", prompt="सही अर्थ चुनें", source_text=en)
        else:          # Hindi word shown, pick the English word
            opts, ans = [en] + [w[0] for w in wrong], en
            ex = Exercise(type="multiple_choice", prompt="इसका अंग्रेज़ी अर्थ चुनें", source_text=hi)
        rng.shuffle(opts)
        ex.options, ex.answers = _options(opts, ans), _answers(ans)
        return ex

    def match() -> Exercise:
        ex = Exercise(type="match_pairs", prompt="सही जोड़ियाँ मिलाएँ")
        ex.options = [ExerciseOption(position=i, text=en, pair_text=hi, is_correct=True)
                      for i, (en, hi) in enumerate(rot[:5])]
        return ex

    def translate(s) -> Exercise:
        hi, en = s[0], s[1]
        own = TOKEN.findall(en)
        extra = [t for t in sorted(all_tokens) if t.lower() not in {o.lower() for o in own}]
        tiles = own + rng.sample(extra, min(3, len(extra)))
        rng.shuffle(tiles)
        ex = Exercise(type="translate", prompt="इस वाक्य का अंग्रेज़ी में अनुवाद करें", source_text=hi)
        ex.options, ex.answers = _options(tiles), _answers(en, s[3] if len(s) > 3 else ())
        return ex

    def fill(s) -> Exercise:
        hi, en, blank = s[0], s[1], s[2]
        sentence = re.sub(rf"\b{re.escape(blank)}\b", "____", en, count=1)
        own = {o.lower() for o in TOKEN.findall(en)}
        extra = [t for t in sorted(all_tokens) if t.lower() != blank.lower() and t.lower() not in own]
        opts = [blank] + rng.sample(extra, min(3, len(extra)))
        rng.shuffle(opts)
        ex = Exercise(type="fill_blank", prompt="रिक्त स्थान भरें", source_text=sentence, hint=hi)
        ex.options, ex.answers = _options(opts, blank), _answers(blank)
        return ex

    def type_answer(word) -> Exercise:
        ex = Exercise(type="type_answer", prompt="इसे अंग्रेज़ी में टाइप करें", source_text=word[1])
        ex.answers = _answers(word[0])
        return ex

    return [mcq(rot[0], True), mcq(rot[1], False), match(), translate(sa), fill(sb),
            type_answer(rot[2]), translate(sb), fill(sa)]


def seed_content(db: Session) -> None:
    course = Course(**content.COURSE)
    db.add(course)
    for upos, u in enumerate(content.UNITS, start=1):
        unit = Unit(position=upos, title=u["title"], description=u["description"], color=u["color"])
        course.units.append(unit)       # append from the parent side so the session cascades the save
        for spos, sk in enumerate(u["skills"], start=1):
            skill = Skill(position=spos, title=sk["title"], icon=sk["icon"])
            unit.skills.append(skill)
            for li in range(content.LESSONS_PER_SKILL):
                lesson = Lesson(position=li + 1)
                skill.lessons.append(lesson)
                for pos, ex in enumerate(build_lesson_exercises(sk, li), start=1):
                    ex.position = pos
                    lesson.exercises.append(ex)
    for code, title, desc, icon, metric, threshold, gems in content.ACHIEVEMENTS:
        db.add(Achievement(code=code, title=title, description=desc, icon=icon, metric=metric,
                           threshold=threshold, gem_reward=gems))
    for tier, name, color in content.LEAGUES:
        db.add(League(tier=tier, name=name, color=color))


# ------------------------------------------------------------ demo learner
# (skill index, lesson position, days ago, mistakes): two finished skills, one lesson into the third,
# active on each of the last four days -> a 4-day streak.
DEMO_HISTORY = [(0, 1, 3, 1), (0, 2, 3, 0), (0, 3, 2, 0), (1, 1, 2, 2), (1, 2, 1, 0), (1, 3, 1, 0), (2, 1, 0, 0)]


def _at(day: date, hour: int) -> datetime:
    return datetime.combine(day, time(hour, 0))


def restore_demo_history(db: Session, user: User) -> None:
    """Give a (freshly wiped) learner the sample progress, dated relative to *their* today."""
    today = effective_today(user)
    skills = ordered_skills(db)
    for n, (si, pos, ago, mistakes) in enumerate(DEMO_HISTORY):
        skill = skills[si]
        lesson = skill.lessons[pos - 1]
        xp = rules.XP_LESSON + (rules.XP_LESSON_PERFECT_BONUS if mistakes == 0 else 0)
        day = today - timedelta(days=ago)
        db.add(StudySession(user_id=user.id, kind="lesson", status="completed", lesson_id=lesson.id,
                            skill_id=skill.id, xp_earned=xp, gems_earned=rules.GEMS_LESSON, correct_count=8,
                            mistakes=mistakes, duration_sec=150, started_at=_at(day, 8 + n),
                            completed_at=_at(day, 8 + n), activity_date=day))
        user.total_xp += xp
        prog = db.scalar(select(UserSkillProgress).filter_by(user_id=user.id, skill_id=skill.id))
        if prog is None:
            db.add(UserSkillProgress(user_id=user.id, skill_id=skill.id, lessons_completed=pos))
        else:
            prog.lessons_completed = pos
        db.flush()
    user.streak = user.longest_streak = 4
    user.last_active_date = today
    user.hearts = 4
    check_achievements(db, user)
    user.gems = 500        # badge rewards are not added to the seeded starting balance


def refresh_rivals(db: Session) -> None:
    """(Re)create the rivals' XP so the weekly leaderboard is populated for the *current* week.
    Each rival's total_xp equals the sum of their sessions (no drifting counters)."""
    learner = db.get(User, 1)
    today = effective_today(learner) if learner else date.today()
    week_days = [today - timedelta(days=d) for d in range(today.weekday() + 1)]   # Monday .. today
    rivals = list(db.scalars(select(User).where(User.username.in_([r[0] for r in content.RIVALS]))))
    db.execute(delete(StudySession).where(StudySession.user_id.in_([r.id for r in rivals])))
    weekly = {name: xp for name, _, _, xp in content.RIVALS}
    for rival in rivals:
        week_xp = weekly[rival.username]
        shares = [week_xp // len(week_days)] * len(week_days)
        shares[0] += week_xp - sum(shares)
        history = [(today - timedelta(days=30), week_xp * 2)] + list(zip(week_days, shares))
        for day, xp in history:
            if xp > 0:
                db.add(StudySession(user_id=rival.id, kind="practice", status="completed", xp_earned=xp,
                                    correct_count=xp // 2, started_at=_at(day, 12), completed_at=_at(day, 12),
                                    activity_date=day))
        rival.total_xp = sum(xp for _, xp in history)


def seed_people(db: Session) -> None:
    bronze = db.scalar(select(League).where(League.tier == 1))
    learner = User(username="learner", display_name="You", avatar_color="#58cc02", league_id=bronze.id,
                   daily_goal_xp=20)
    db.add(learner)
    db.flush()
    restore_demo_history(db, learner)
    for username, name, color, _ in content.RIVALS:
        db.add(User(username=username, display_name=name, avatar_color=color, league_id=bronze.id, daily_goal_xp=20))
    db.flush()
    refresh_rivals(db)


def seed() -> None:
    """Assumes the schema exists (see app.migrate)."""
    with SessionLocal() as db:
        if db.scalar(select(Course.id)) is not None:
            return
        seed_content(db)
        db.flush()
        seed_people(db)
        db.commit()


if __name__ == "__main__":
    from .migrate import upgrade_database
    upgrade_database()
    seed()
    print("Database seeded.")
