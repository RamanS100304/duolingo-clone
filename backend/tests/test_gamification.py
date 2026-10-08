"""Practice, timed, legendary, streak, chests, leaderboard, profile, quests and dev tools."""
from conftest import (backdate_session, correct_answer, current_lesson_id, node, sessions_of, solve_all,
                      solve_exercise, start, wrong_answer)


def finish_lesson(c):
    session = start(c, lesson_id=current_lesson_id(c)).json()
    solve_all(c, session)
    return c.post(f"/api/sessions/{session['id']}/complete").json()


# ------------------------------------------------------------------ practice
def test_practice_costs_no_hearts_and_earns_one(client):
    session = start(client, "practice").json()
    ex = session["exercises"][0]
    r = client.post(f"/api/sessions/{session['id']}/answers", json={"exercise_id": ex["id"], "answer": wrong_answer()})
    assert r.json()["hearts"] == 4
    assert client.post(f"/api/sessions/{session['id']}/complete").status_code == 409   # must actually finish
    solve_all(client, session)
    done = client.post(f"/api/sessions/{session['id']}/complete").json()
    assert done["xp_earned"] == 5 and done["user"]["hearts"] == 5


def test_practice_needs_a_finished_lesson(client):
    client.post("/api/dev/reset", json={"mode": "empty"})
    r = start(client, "practice")
    assert r.status_code == 400 and r.json()["code"] == "nothing_to_practice"


# --------------------------------------------------------------------- timed
def test_timed_uses_server_side_counts_and_clock(client):
    session = start(client, "timed").json()
    sid = session["id"]
    assert session["time_limit_sec"] == 120
    assert all(e["type"] != "match_pairs" for e in session["exercises"])
    ex = session["exercises"]
    for e in ex[:3]:
        solve_exercise(client, session, e)
    # one try per question in timed mode
    again = client.post(f"/api/sessions/{sid}/answers", json={"exercise_id": ex[3]["id"], "answer": wrong_answer()})
    assert again.status_code == 200
    assert client.post(f"/api/sessions/{sid}/answers", json={"exercise_id": ex[3]["id"], "answer": "x"}).status_code == 409
    # finishing early with unanswered questions is refused while the clock runs
    assert client.post(f"/api/sessions/{sid}/complete").status_code == 409
    backdate_session(sid, 200)                                    # the two minutes are over
    late = client.post(f"/api/sessions/{sid}/answers", json={"exercise_id": ex[4]["id"], "answer": correct_answer(ex[4]["id"])})
    assert late.status_code == 409 and late.json()["code"] == "time_up"
    done = client.post(f"/api/sessions/{sid}/complete").json()
    assert done["correct_count"] == 3 and done["xp_earned"] == 6 and done["gems_earned"] == 0


# ----------------------------------------------------------------- legendary
def test_legendary_requires_finished_skill(client):
    numbers = node(client, "Numbers")
    r = start(client, "legendary", skill_id=numbers["id"])
    assert r.status_code == 403 and r.json()["code"] == "locked"
    assert start(client, "legendary").status_code == 422           # skill_id is required


def test_legendary_fails_after_two_mistakes(client):
    greetings = node(client, "Greetings")
    session = start(client, "legendary", skill_id=greetings["id"]).json()
    sid = session["id"]
    assert session["max_mistakes"] == 1
    for ex in session["exercises"][:2]:
        r = client.post(f"/api/sessions/{sid}/answers", json={"exercise_id": ex["id"], "answer": ""}).json()
    assert r["status"] == "failed"
    r = client.post(f"/api/sessions/{sid}/complete")
    assert r.status_code == 409 and r.json()["code"] == "challenge_failed"
    assert client.get("/api/me").json()["total_xp"] == 95


def test_legendary_success_awards_crown_and_badge(client):
    greetings = node(client, "Greetings")
    session = start(client, "legendary", skill_id=greetings["id"]).json()
    solve_all(client, session)
    done = client.post(f"/api/sessions/{session['id']}/complete").json()
    assert done["xp_earned"] == 40 and done["gems_earned"] == 20
    assert any(a["title"] == "Legend" for a in done["new_achievements"])
    assert node(client, "Greetings")["legendary"] is True


# -------------------------------------------------------------------- streak
def test_streak_increments_and_resets_with_simulated_days(client):
    done = finish_lesson(client)
    assert done["streak"] == {"before": 4, "after": 4, "increased": False}     # already active today
    client.post("/api/dev/advance-day", json={"days": 1})
    done = finish_lesson(client)
    assert done["streak"] == {"before": 4, "after": 5, "increased": True}
    assert client.post("/api/dev/advance-day", json={"days": 3}).json()["streak"] == 0
    done = finish_lesson(client)
    assert done["streak"]["after"] == 1


def test_timezone_setting(client):
    assert client.patch("/api/me", json={"timezone": "Mars/Olympus"}).status_code == 422
    me = client.patch("/api/me", json={"timezone": "America/New_York"}).json()
    assert me["timezone"] == "America/New_York"


def test_daily_goal_setting(client):
    assert client.patch("/api/me", json={"daily_goal_xp": 1000}).status_code == 422
    assert client.patch("/api/me", json={"daily_goal_xp": 10}).json()["daily_goal_xp"] == 10


# --------------------------------------------------------------------- path
def test_chest_opens_once_and_only_when_reached(client):
    units = client.get("/api/path").json()["units"]
    chest = next(n for n in units[0]["nodes"] if n["type"] == "chest")
    assert chest["state"] == "available"
    r = client.post(f"/api/units/{chest['id']}/chest").json()
    assert r["gems_earned"] == 20 and r["user"]["gems"] == 520
    assert client.post(f"/api/units/{chest['id']}/chest").status_code == 409
    locked = next(n for n in units[1]["nodes"] if n["type"] == "chest")
    assert client.post(f"/api/units/{locked['id']}/chest").status_code == 403


def test_unit_review_needs_complete_unit(client):
    units = client.get("/api/path").json()["units"]
    assert start(client, "practice", unit_id=units[0]["id"]).status_code == 403


# ------------------------------------------------------------ social / data
def test_leaderboard_is_weekly_xp_of_my_league(client):
    lb = client.get("/api/leaderboard").json()
    assert lb["league"] == "Bronze League" and len(lb["entries"]) == 15
    xps = [e["xp"] for e in lb["entries"]]
    assert xps == sorted(xps, reverse=True)
    me = next(e for e in lb["entries"] if e["is_me"])
    finish_lesson(client)
    me_after = next(e for e in client.get("/api/leaderboard").json()["entries"] if e["is_me"])
    assert me_after["xp"] == me["xp"] + 15


def test_rival_totals_match_their_sessions(client):
    for user_id in range(2, 16):
        total = sum(s.xp_earned for s in sessions_of(user_id) if s.status == "completed")
        assert client.get("/api/me", headers={"X-User-Id": str(user_id)}).json()["total_xp"] == total


def test_profile_and_quests(client):
    profile = client.get("/api/profile").json()
    assert len(profile["achievements"]) == 10 and profile["stats"]["skills_completed"] == 2
    quests = {q["id"]: q for q in client.get("/api/quests").json()["quests"]}
    assert quests["lessons"]["progress"] == 1 and not quests["lessons"]["done"]
    finish_lesson(client)
    quests = {q["id"]: q for q in client.get("/api/quests").json()["quests"]}
    assert quests["lessons"]["done"] and quests["goal"]["done"]


def test_reset_to_demo_and_to_empty(client):
    finish_lesson(client)
    assert client.post("/api/dev/reset", json={"mode": "empty"}).json()["total_xp"] == 0
    assert client.get("/api/path").json()["units"][0]["nodes"][0]["state"] == "available"
    demo = client.post("/api/dev/reset", json={"mode": "demo"}).json()
    assert (demo["streak"], demo["total_xp"], demo["hearts"]) == (4, 95, 4)
