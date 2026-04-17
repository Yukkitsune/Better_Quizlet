import sqlite3
from pathlib import Path
from core import config


def init_db() -> sqlite3.Connection:
    db_path = Path(config.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS decks (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            tags TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY,
            deck_id INTEGER,
            front TEXT NOT NULL,
            back TEXT NOT NULL,
            difficulty_hint TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(deck_id) REFERENCES decks(id) ON DELETE CASCADE,
            UNIQUE(deck_id, front)
        );
        CREATE TABLE IF NOT EXISTS progress (
            card_id INTEGER,
            user_id INTEGER,
            interval INTEGER DEFAULT 1,
            ease_factor REAL DEFAULT 2.5,
            repetitions INTEGER DEFAULT 0,
            last_review TEXT,
            next_review TEXT,
            status TEXT DEFAULT 'new' CHECK(status IN ('new', 'learning', 'review', 'mastered')),
            correct_count INTEGER DEFAULT 0,
            total_attempts INTEGER DEFAULT 0,
            PRIMARY KEY(card_id, user_id),
            FOREIGN KEY(card_id) REFERENCES cards(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_progress_due ON progress(user_id, next_review);
        CREATE INDEX IF NOT EXISTS idx_cards_deck ON cards(deck_id);
        """
    )
    return conn


def close_db(conn: sqlite3.Connection) -> None:
    if conn:
        conn.close()
