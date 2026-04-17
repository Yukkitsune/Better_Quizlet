from db.models import DeckCreate, CardImport, ProgressUpdate
from datetime import datetime, timedelta, timezone
import sqlite3


def create_deck(conn: sqlite3.Connection, deck: DeckCreate) -> int:
    try:
        cursor = conn.execute(
            "INSERT INTO decks(name, description, tags) VALUES (?, ?, ?)",
            (deck.name, deck.description, deck.tags),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return 0


def import_cards(
    conn: sqlite3.Connection, deck_id: int, cards: list[CardImport]
) -> int:
    cursor = conn.execute("SELECT 1 FROM decks WHERE id=?", (deck_id,))
    if cursor.fetchone() is None:
        return 0
    card_list = [(deck_id, c.front, c.back, c.difficulty_hint) for c in cards]
    cursor = conn.executemany(
        "INSERT OR IGNORE INTO cards (deck_id, front, back, difficulty_hint) VALUES (?, ?, ?, ?)",
        card_list,
    )
    conn.commit()
    return cursor.rowcount


def get_due_cards(
    conn: sqlite3.Connection, user_id: int, limit: int = 20
) -> list[dict]:
    cursor = conn.execute(
        """
        SELECT c.id, c.front, c.back, c.deck_id, 
               p.status, p.interval, p.ease_factor
        FROM cards c
        LEFT JOIN progress p ON c.id = p.card_id AND p.user_id = ?
        WHERE p.next_review IS NULL OR p.next_review <= datetime('now')
        ORDER BY
            CASE
                WHEN p.status IS NULL OR p.status = 'new' THEN 1
                WHEN p.status = 'learning' THEN 2
                WHEN p.status = 'review' THEN 3
                ELSE 4
            END,
            RANDOM()
        LIMIT ?
        """,
        (user_id, limit),
    )
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def update_progress(conn: sqlite3.Connection, update: ProgressUpdate) -> dict:
    cursor = conn.execute(
        "SELECT * FROM progress WHERE card_id=? AND user_id=?",
        (update.card_id, update.user_id),
    )
    row = cursor.fetchone()

    if row is None:
        prog = {
            "card_id": update.card_id,
            "user_id": update.user_id,
            "interval": 1,
            "ease_factor": 2.5,
            "repetitions": 0,
            "last_review": None,
            "next_review": None,
            "status": "new",
            "correct_count": 0,
            "total_attempts": 0,
        }
    else:
        prog = dict(zip([col[0] for col in cursor.description], row))

    now = datetime.now(timezone.utc)
    prog["last_review"] = now.strftime("%Y-%m-%d %H:%M:%S")
    prog["total_attempts"] += 1

    if update.is_correct:
        prog["correct_count"] += 1
        status = prog["status"]

        if status == "new":
            prog["status"] = "learning"
            prog["interval"] = 1
            prog["repetitions"] = 1
        elif status == "learning":
            prog["repetitions"] += 1
            prog["interval"] = 1
            if prog["repetitions"] >= 2:
                prog["status"] = "review"
                prog["interval"] = max(int(prog["ease_factor"]), 1)
        elif status == "review":
            prog["repetitions"] += 1
            prog["interval"] = max(int(prog["interval"] * prog["ease_factor"]), 1)
            prog["ease_factor"] = min(prog["ease_factor"] + 0.05, 3.0)
        elif status == "mastered":
            prog["interval"] = max(int(prog["interval"] * prog["ease_factor"]), 1)
    else:
        prog["interval"] = 1
        prog["repetitions"] = 0
        prog["ease_factor"] = max(prog["ease_factor"] - 0.1, 1.3)
        prog["status"] = "learning" if prog["status"] != "new" else "new"

    if prog["status"] == "review" and prog["interval"] >= 30:
        prog["status"] = "mastered"

    prog["next_review"] = (now + timedelta(days=prog["interval"])).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conn.execute(
        """INSERT OR REPLACE INTO progress
           (card_id, user_id, interval, ease_factor, repetitions, last_review, next_review, status, correct_count, total_attempts)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            prog["card_id"],
            prog["user_id"],
            prog["interval"],
            prog["ease_factor"],
            prog["repetitions"],
            prog["last_review"],
            prog["next_review"],
            prog["status"],
            prog["correct_count"],
            prog["total_attempts"],
        ),
    )
    conn.commit()
    return prog
