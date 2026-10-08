"""Runtime settings, all overridable with environment variables."""
import os
import secrets


def _flag(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


# sqlite:///./duolingo.db locally; on a host with a volume use e.g. sqlite:////data/duolingo.db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./duolingo.db")

# Comma-separated list of allowed frontend origins ("*" = any).
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]

# Signs the match-pairs tokens. Set it in production so tokens survive a restart.
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)

# Testing aids (simulate a day / reset the demo learner). On by default so reviewers can test
# streak logic; set ENABLE_DEV_TOOLS=false to remove the /api/dev routes entirely.
ENABLE_DEV_TOOLS = _flag("ENABLE_DEV_TOOLS", True)

# Learner day boundaries (streak, daily goal) use this zone until the browser reports its own.
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Asia/Kolkata")
