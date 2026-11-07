import sqlite3
import datetime
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent.parent / "logs_interactions.db"

def init_db(db_path: Path = DB_PATH):
    """Initialise la table de journalisation SQLite si elle n'existe pas."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interaction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            prompt_version TEXT NOT NULL,
            user_question TEXT NOT NULL,
            raw_response TEXT,
            is_valid_json INTEGER NOT NULL, -- 1 = valide, 0 = invalide
            latency_ms REAL,
            error_message TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_interaction(
    prompt_version: str,
    user_question: str,
    raw_response: Optional[str],
    is_valid_json: bool,
    latency_ms: float,
    error_message: Optional[str] = None,
    db_path: Path = DB_PATH
):
    """Enregistre chaque requête/réponse dans SQLite pour une traçabilité à 100%."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO interaction_logs (
            timestamp, prompt_version, user_question, raw_response, 
            is_valid_json, latency_ms, error_message
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.datetime.now(datetime.timezone.utc).isoformat(),
        prompt_version,
        user_question,
        raw_response,
        1 if is_valid_json else 0,
        latency_ms,
        error_message
    ))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Base SQLite initialisée avec succès :", DB_PATH)
