"""Every test gets a fresh, migrated and seeded SQLite database."""
import os
import tempfile
from pathlib import Path

DB_FILE = Path(tempfile.mkdtemp()) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{DB_FILE}"
os.environ["SECRET_KEY"] = "test-secret"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app.database import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Exercise, StudySession  # noqa: E402
from app.services.answers import pair_token  # noqa: E402


@pytest.fixture
def client():
    engine.dispose()
    for suffix in ("", "-wal", "-shm"):
        Path(f"{DB_FILE}{suffix}").unlink(missing_ok=True)
    with TestClient(app) as c:          # lifespan runs migrations + seed
        yield c


@pytest.fixture
def db():
    with SessionLocal() as s:
        yield s


# ------------------------------------------------------------------ helpers
def correct_answer(exercise_id: int) -> str:
    with SessionLocal() as s:
        return s.get(Exercise, exercise_id).primary_answer


def wrong_answer() -> str:
    return "definitely wrong"


def solve_exercise(c, session: dict, ex: dict) -> None:
    sid = session["id"]
    if ex["type"] == "match_pairs":
        for left in ex["pairs"]["left"]:
            r = c.post(f"/api/sessions/{sid}/pairs", json={
                "exercise_id": ex["id"], "left_id": int(left["id"]), "right_id": pair_token(sid, int(left["id"]))})
            assert r.status_code == 200 and r.json()["correct"], r.text
    else:
        r = c.post(f"/api/sessions/{sid}/answers", json={"exercise_id": ex["id"], "answer": correct_answer(ex["id"])})
        assert r.status_code == 200 and r.json()["correct"], r.text


def solve_all(c, session: dict) -> None:
    for ex in session["exercises"]:
        solve_exercise(c, session, ex)


def start(c, kind="lesson", **ids):
    return c.post("/api/sessions", json={"kind": kind, **ids})


def current_lesson_id(c) -> int:
    for unit in c.get("/api/path").json()["units"]:
        for node in unit["nodes"]:
            if node["type"] == "skill" and node["is_current"]:
                return node["next_lesson_id"]
    raise AssertionError("no current lesson")


def node(c, title: str) -> dict:
    return next(n for u in c.get("/api/path").json()["units"] for n in u["nodes"] if n["title"] == title)


def backdate_session(session_id: int, seconds: int) -> None:
    from datetime import timedelta
    with SessionLocal() as s:
        row = s.get(StudySession, session_id)
        row.started_at = row.started_at - timedelta(seconds=seconds)
        s.commit()


def sessions_of(user_id: int) -> list[StudySession]:
    with SessionLocal() as s:
        return list(s.scalars(select(StudySession).where(StudySession.user_id == user_id)))
