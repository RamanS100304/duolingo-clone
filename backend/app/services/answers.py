"""Answer checking and the exercise payload sent to the client (which never contains answers)."""
import hashlib
import hmac
import random
import unicodedata

from ..config import SECRET_KEY
from ..models import Exercise

TYPED_EXERCISES = ("type_answer",)     # free-text answers get typo tolerance
TYPO_MIN_LENGTH = 4


def normalize(text: str) -> str:
    """Case/punctuation/whitespace-insensitive form used to compare answers."""
    text = unicodedata.normalize("NFC", text or "").lower()
    text = "".join(c for c in text if not unicodedata.category(c).startswith("P"))
    return " ".join(text.split())


def edit_distance(a: str, b: str) -> int:
    """Levenshtein distance (small strings only)."""
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def check(ex: Exercise, answer: str) -> tuple[bool, bool]:
    """Returns (correct, typo). Typed answers one letter away from an accepted answer count as
    correct-with-a-typo, as on Duolingo. Match-pairs are verified pair by pair instead."""
    accepted = {normalize(a.text) for a in ex.answers}
    if not accepted:
        return False, False
    given = normalize(answer)
    if given in accepted:
        return True, False
    if ex.type in TYPED_EXERCISES and len(given) >= TYPO_MIN_LENGTH:
        if any(len(a) >= TYPO_MIN_LENGTH and edit_distance(given, a) == 1 for a in accepted):
            return True, True
    return False, False


# ------------------------------------------------------------- match pairs
def pair_token(session_id: int, option_id: int) -> str:
    """Opaque id for the right-hand tile of a pair. Only the server can link it to its left tile."""
    msg = f"{session_id}:{option_id}".encode()
    return "r" + hmac.new(SECRET_KEY.encode(), msg, hashlib.sha256).hexdigest()[:12]


def pair_matches(session_id: int, left_id: int, right_token: str) -> bool:
    return hmac.compare_digest(pair_token(session_id, left_id), right_token)


def serialize_exercise(ex: Exercise, session_id: int) -> dict:
    """Exercise payload for the client. Never includes the correct answer."""
    out = {"id": ex.id, "type": ex.type, "prompt": ex.prompt, "source_text": ex.source_text,
           "hint": ex.hint, "options": None, "pairs": None}
    if ex.type == "match_pairs":
        left = [{"id": str(o.id), "text": o.text} for o in ex.options]
        right = [{"id": pair_token(session_id, o.id), "text": o.pair_text} for o in ex.options]
        random.Random(session_id * 100_003 + ex.id).shuffle(right)
        out["pairs"] = {"left": left, "right": right}
    else:
        out["options"] = [{"id": str(o.id), "text": o.text} for o in ex.options]
    return out
