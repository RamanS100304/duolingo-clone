# Deploying for reviewers

Backend → **Railway** (FastAPI + SQLite on a persistent volume, so progress survives restarts).
Frontend → **Vercel** (Next.js). Both are on the assignment's list of hosts. Total time is about 20 minutes.

> Why not Render's free tier? Free Render services can't attach a disk, so the SQLite file would be wiped on every restart, which breaks "all progress must persist". `render.yaml` is included as an alternative on a paid Render instance with a disk.

---

## 1. Push the code to a public GitHub repo

```bash
cd duolingo-clone
git init
git add .
git commit -m "Duolingo clone: Next.js + FastAPI + SQLite"
git branch -M main
git remote add origin https://github.com/<you>/duolingo-clone.git   # create an empty PUBLIC repo first
git push -u origin main
```
Check on GitHub that the repo root shows `frontend/`, `backend/`, `README.md` and `DEPLOY.md`, and that there is **no** `node_modules`, `.venv` or `*.db` (the `.gitignore` handles this).

## 2. Backend on Railway

1. Sign in at **railway.com** with GitHub → **New Project → Deploy from GitHub repo** → pick the repo.
2. Open the created service → **Settings**:
   * **Root Directory:** `backend`
   * **Config file path** (Config-as-code): `/backend/railway.json`. Railway does *not* look inside the root directory for it. This sets the start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT` and the `/health` check.
3. **Add a volume:** right-click the service on the canvas (or `⌘K` → *Volume*) → attach it to the service → **Mount path `/data`**.
4. **Variables** tab → add:
   | Name | Value |
   |---|---|
   | `DATABASE_URL` | `sqlite:////data/duolingo.db`  ← four slashes = absolute path on the volume |
   | `SECRET_KEY` | any long random string (e.g. output of `python -c "import secrets;print(secrets.token_hex(32))"`) |
   | `CORS_ORIGINS` | `*` for now (tightened in step 4) |
   | `ENABLE_DEV_TOOLS` | `true` (lets reviewers use *Simulate next day*) |
5. **Settings → Networking → Generate Domain**. You get something like `https://duolingo-clone-production.up.railway.app`.
6. Wait for the deploy to turn green, then open:
   * `https://<api-domain>/health` → `{"status":"ok"}`
   * `https://<api-domain>/docs` → Swagger UI
   * `https://<api-domain>/api/me` → the learner JSON (`"streak": 4`, `"total_xp": 95`)

Python 3.13 is selected by `backend/.python-version`, and dependencies come from `backend/requirements.txt`. On first boot the app runs the Alembic migrations and seeds the database on the volume.

> **Cost:** Railway's trial gives a one-time $5 credit for 30 days, and volumes (up to 0.5 GB) are allowed. This app uses well under that, so it covers the interview window. To keep it online longer, upgrade to Hobby ($5/month); trial volumes are deleted 30 days after the trial credit expires.

## 3. Frontend on Vercel

1. Sign in at **vercel.com** with GitHub → **Add New → Project** → import the same repo.
2. **Root Directory:** `frontend` (framework is auto-detected as Next.js).
3. **Environment Variables:** `NEXT_PUBLIC_API_URL` = `https://<api-domain>/api`. Include the `/api` suffix and no trailing slash.
4. **Deploy** → you get `https://<project>.vercel.app`.

`NEXT_PUBLIC_*` values are baked in at build time, so if you change the variable later, **Redeploy** the project.

## 4. Lock CORS to your frontend (optional but tidy)

Back on Railway → Variables → `CORS_ORIGINS` = `https://<project>.vercel.app` (comma-separate several origins). Railway redeploys automatically. The volume keeps the data.

## 5. Smoke-test the live app (5 minutes)

- [ ] `/learn` shows 3 units, two gold skills, an available chest, and the frog next to **Numbers**
- [ ] Open the chest → "+20 gems"
- [ ] Do a lesson: answer one wrong (heart drops, red feedback bar), finish → **Lesson Complete!** with XP
- [ ] **Refresh the page**: XP, hearts and the path are unchanged (persistence)
- [ ] In Railway, **Restart** the service, then refresh the site: progress is still there (volume)
- [ ] More → **Simulate next day** → finish a lesson → the streak screen shows 5
- [ ] Leaderboard, Quests, Shop, Profile and dark mode (More → Preferences) all load
- [ ] On a phone: bottom tab bar, path and lesson fit the screen

## 6. Before you share the links / the day of the interview

* More → Testing tools → **Restore demo learner**. This re-dates the sample history to *today* (4-day streak, daily goal partly done) and refreshes the rivals' weekly XP, so reviewers see a lively state rather than a broken streak from deploy day.
* Put both URLs at the top of `README.md` (replace the `<your-app>` placeholders), commit and push.
* Submit: the GitHub repo URL and the Vercel URL.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Site says "Waking up the server…" forever | `NEXT_PUBLIC_API_URL` is wrong or missing `/api`. Fix it in Vercel, then **Redeploy** |
| Browser console shows a CORS error | Add the exact Vercel origin (with `https://`, no trailing slash) to `CORS_ORIGINS`, or use `*` |
| Railway deploy fails on start | Check Root Directory = `backend` and Config file = `/backend/railway.json`; the deploy logs should end with `Application startup complete` |
| Progress resets after a restart | The volume isn't mounted at `/data`, or `DATABASE_URL` doesn't use 4 slashes (`sqlite:////data/duolingo.db`) |
| `unable to open database file` | Same as above: the folder in `DATABASE_URL` must be the volume mount path |
| Want a completely fresh database | Railway → service → Volume → wipe, or use More → Testing tools → **Start from scratch** |
