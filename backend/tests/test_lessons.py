"""The lesson loop: payloads, answers, hearts, completion and the integrity rules."""
import json

from conftest import correct_answer, current_lesson_id, solve_all, solve_exercise, start, wrong_answer


def test_seeded_learner_is_immediately_usable(client):
    me = client.get("/api/me").json()
    assert (me["streak"], me["hearts"], me["total_xp"], me["daily_xp"]) == (4, 4, 95, 15)
    assert me["league"] == "Bronze League" and me["timezone"] == "Asia/Kolkata"
    units = client.get("/api/path").json()["units"]
    assert len(units) == 3 and all(len([n for n in u["nodes"] if n["type"] == "skill"]) == 4 for u in units)
    states = [n["state"] for n in units[0]["nodes"]]
    assert states == ["completed", "completed", "available", "available", "locked", "locked"]   # skill, skill, chest...


def test_payload_never_contains_answers(client):
    session = start(client, lesson_id=current_lesson_id(client)).json()
    text = json.dumps(session)
    assert '"answer' not in text and "is_correct" not in text
    for ex in session["exercises"]:
        if ex["type"] == "match_pairs":
            left = {o["id"] for o in ex["pairs"]["left"]}
            right = {o["id"] for o in ex["pairs"]["right"]}
            assert not left & right, "right tiles must not reuse the left ids"
            assert all(r.startswith("r") and len(r) == 13 for r in right)
        elif ex["type"] in ("multiple_choice", "fill_blank"):
            assert correct_answer(ex["id"]) in [o["text"] for o in ex["options"]]


def test_full_lesson_flow(client):
    lesson_id = current_lesson_id(client)
    session = start(client, lesson_id=lesson_id).json()
    sid, first = session["id"], session["exercises"][0]

    wrong = client.post(f"/api/sessions/{sid}/answers", json={"exercise_id": first["id"], "answer": wrong_answer()}).json()
    assert wrong["correct"] is False and wrong["hearts"] == 3 and wrong["mistakes"] == 1
    assert wrong["correct_answer"] == correct_answer(first["id"])

    # the missed exercise must still be solved before the lesson can finish
    assert client.post(f"/api/sessions/{sid}/complete").status_code == 409
    solve_all(client, session)
    done = client.post(f"/api/sessions/{sid}/complete").json()
    assert done["xp_earned"] == 10 and done["mistakes"] == 1 and done["perfect"] is False
    assert done["user"]["total_xp"] == 105 and done["daily_goal_reached"] is True
    assert done["accuracy"] == round(100 * 8 / 9)
    assert client.post(f"/api/sessions/{sid}/complete").status_code == 409        # can't cash in twice
    assert current_lesson_id(client) == lesson_id + 1


def test_perfect_lesson_bonus(client):
    session = start(client, lesson_id=current_lesson_id(client)).json()
    solve_all(client, session)
    done = client.post(f"/api/sessions/{session['id']}/complete").json()
    assert done["xp_earned"] == 15 and done["perfect"] is True and done["accuracy"] == 100


def test_cannot_complete_without_playing(client):
    session = start(client, lesson_id=current_lesson_id(client)).json()
    r = client.post(f"/api/sessions/{session['id']}/complete")
    assert r.status_code == 409 and r.json()["code"] == "unfinished"
    assert client.get("/api/me").json()["total_xp"] == 95


def test_old_trust_the_client_endpoints_are_gone(client):
    assert client.post("/api/lessons/1/complete", json={"mistakes": 0, "correct": 0}).status_code in (404, 405)
    assert client.post("/api/sessions/complete", json={"kind": "timed", "correct": 1000}).status_code in (404, 405, 422)


def test_skip_counts_as_a_mistake(client):
    session = start(client, lesson_id=current_lesson_id(client)).json()
    ex = session["exercises"][2]                                  # match-pairs can be skipped too
    r = client.post(f"/api/sessions/{session['id']}/answers", json={"exercise_id": ex["id"], "answer": ""}).json()
    assert r["correct"] is False and r["hearts"] == 3


def test_locked_skill_cannot_be_started(client):
    path = client.get("/api/path").json()["units"]
    locked = next(n for n in path[1]["nodes"] if n["type"] == "skill")
    assert locked["state"] == "locked"
    from app.database import SessionLocal
    from app.models import Skill
    with SessionLocal() as s:
        lesson_id = s.get(Skill, locked["id"]).lessons[0].id
    r = start(client, lesson_id=lesson_id)
    assert r.status_code == 403 and r.json()["code"] == "locked"


def test_out_of_hearts_blocks_lessons_until_refill(client):
    session = start(client, lesson_id=current_lesson_id(client)).json()
    sid, ex = session["id"], session["exercises"][0]
    for expected in (3, 2, 1, 0):
        r = client.post(f"/api/sessions/{sid}/answers", json={"exercise_id": ex["id"], "answer": wrong_answer()})
        assert r.json()["hearts"] == expected
    blocked = client.post(f"/api/sessions/{sid}/answers", json={"exercise_id": ex["id"], "answer": correct_answer(ex["id"])})
    assert blocked.status_code == 403 and blocked.json()["code"] == "out_of_hearts"
    assert start(client, lesson_id=current_lesson_id(client)).status_code == 403

    assert client.post("/api/hearts/refill").json()["hearts"] == 5
    assert client.post("/api/hearts/refill").json()["code"] == "hearts_full"
    solve_exercise(client, session, ex)                        # the same session continues after a refill


def test_answers_are_limited_to_the_session(client):
    session = start(client, lesson_id=current_lesson_id(client)).json()
    sid = session["id"]
    in_session = {e["id"] for e in session["exercises"]}
    outsider = next(i for i in range(1, 300) if i not in in_session)
    r = client.post(f"/api/sessions/{sid}/answers", json={"exercise_id": outsider, "answer": "x"})
    assert r.status_code == 404 and r.json()["code"] == "not_in_session"
    # another learner can't use (or even see) this session
    r = client.post(f"/api/sessions/{sid}/answers", headers={"X-User-Id": "2"},
                    json={"exercise_id": session["exercises"][0]["id"], "answer": "x"})
    assert r.status_code == 404


def test_solved_exercise_cannot_be_answered_again(client):
    session = start(client, lesson_id=current_lesson_id(client)).json()
    ex = session["exercises"][0]
    solve_exercise(client, session, ex)
    r = client.post(f"/api/sessions/{session['id']}/answers", json={"exercise_id": ex["id"], "answer": "x"})
    assert r.status_code == 409


def test_match_pairs_tokens(client):
    from app.services.answers import pair_token
    session = start(client, lesson_id=current_lesson_id(client)).json()
    sid = session["id"]
    ex = next(e for e in session["exercises"] if e["type"] == "match_pairs")
    l0, l1 = (int(o["id"]) for o in ex["pairs"]["left"][:2])

    bad = client.post(f"/api/sessions/{sid}/pairs", json={"exercise_id": ex["id"], "left_id": l0,
                                                          "right_id": pair_token(sid, l1)}).json()
    assert bad["correct"] is False and bad["mistakes"] == 1 and bad["hearts"] == 4   # no heart lost
    # a token from another session doesn't work here
    other = client.post(f"/api/sessions/{sid}/pairs", json={"exercise_id": ex["id"], "left_id": l0,
                                                            "right_id": pair_token(sid + 1, l0)}).json()
    assert other["correct"] is False
    solve_exercise(client, session, ex)
    state = client.post(f"/api/sessions/{sid}/answers", json={"exercise_id": ex["id"], "answer": ""})
    assert state.status_code == 409                                                   # already solved


def test_typo_tolerance_only_for_typed_answers(client):
    session = start(client, lesson_id=current_lesson_id(client)).json()
    typed = next(e for e in session["exercises"] if e["type"] == "type_answer")
    answer = correct_answer(typed["id"])
    sid = session["id"]
    if len(answer) >= 4:
        typo = answer[:-1] + ("x" if answer[-1] != "x" else "y")
        r = client.post(f"/api/sessions/{sid}/answers", json={"exercise_id": typed["id"], "answer": typo}).json()
        assert r["correct"] is True and r["typo"] is True
    from app.services.answers import check
    from app.models import Exercise, ExerciseAnswer
    ex = Exercise(type="type_answer", answers=[ExerciseAnswer(text="grandmother", is_primary=True)])
    assert check(ex, "Grandmothr") == (True, True)
    assert check(ex, "grandfather") == (False, False)
    mcq = Exercise(type="multiple_choice", answers=[ExerciseAnswer(text="water", is_primary=True)])
    assert check(mcq, "watr") == (False, False)


def test_starting_a_new_session_abandons_the_open_one(client):
    first = start(client, lesson_id=current_lesson_id(client)).json()
    start(client, lesson_id=current_lesson_id(client))
    r = client.post(f"/api/sessions/{first['id']}/answers", json={"exercise_id": first["exercises"][0]["id"], "answer": "x"})
    assert r.status_code == 409 and r.json()["code"] == "session_closed"


def test_quit_abandons_session(client):
    session = start(client, lesson_id=current_lesson_id(client)).json()
    assert client.post(f"/api/sessions/{session['id']}/abandon").status_code == 204
    assert client.post(f"/api/sessions/{session['id']}/complete").status_code == 409
