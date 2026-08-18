import json
import os
import sqlite3
from pathlib import Path
from typing import cast
from uuid import uuid4

from .game import LEGACY_COLOR_VALUES
from .types import Attempt, Game, Stats


def _default_db_path() -> Path:
    """Retourne l'emplacement persistant par défaut de la base SQLite."""
    data_home = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return data_home / "mastermind" / "mastermind.db"


DB_PATH = Path(os.getenv("MASTERMIND_DB", _default_db_path()))


def _connect() -> sqlite3.Connection:
    """Ouvre une connexion SQLite configurée pour retourner des lignes nommées."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Crée le schéma et applique les migrations légères nécessaires."""
    with _connect() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS games (
                id TEXT PRIMARY KEY,
                mode TEXT NOT NULL,
                code_length INTEGER NOT NULL DEFAULT 4,
                secret_json TEXT NOT NULL,
                attempts_json TEXT NOT NULL DEFAULT '[]',
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                duration_seconds INTEGER NOT NULL DEFAULT 0,
                score INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        columns = {str(row["name"]) for row in db.execute("PRAGMA table_info(games)")}
        if "player_name" not in columns:
            db.execute("ALTER TABLE games ADD COLUMN player_name TEXT")
        if "code_length" not in columns:
            db.execute("ALTER TABLE games ADD COLUMN code_length INTEGER NOT NULL DEFAULT 4")
        db.execute(
            "CREATE INDEX IF NOT EXISTS idx_games_status_started ON games(status, started_at DESC)"
        )


def create_game(
    mode: str,
    secret: list[str],
    started_at: str,
    code_length: int | None = None,
) -> Game:
    """Crée et retourne une nouvelle partie active."""
    game_id = str(uuid4())
    length = code_length if code_length is not None else len(secret)
    with _connect() as db:
        db.execute(
            """
            INSERT INTO games(id, mode, code_length, secret_json, attempts_json, status, started_at)
            VALUES (?, ?, ?, ?, '[]', 'active', ?)
            """,
            (game_id, mode, length, json.dumps(secret), started_at),
        )
    game = get_game(game_id)
    if game is None:
        raise RuntimeError("La partie créée est introuvable")
    return game


def get_game(game_id: str) -> Game | None:
    """Charge une partie par son identifiant, si elle existe."""
    with _connect() as db:
        row = db.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
    return _decode(row) if row else None


def get_current_game() -> Game | None:
    """Retourne la partie active la plus récente, si elle existe."""
    with _connect() as db:
        row = db.execute(
            "SELECT * FROM games WHERE status = 'active' ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
    return _decode(row) if row else None


def save_attempts(game_id: str, attempts: list[Attempt]) -> None:
    """Remplace la liste persistée des tentatives d'une partie."""
    with _connect() as db:
        db.execute(
            "UPDATE games SET attempts_json = ? WHERE id = ?",
            (json.dumps(attempts), game_id),
        )


def finish_game(
    game_id: str,
    *,
    status: str,
    ended_at: str,
    duration_seconds: int,
    score: int,
) -> None:
    """Termine une partie avec son statut, sa durée et son score définitifs."""
    with _connect() as db:
        db.execute(
            """
            UPDATE games
            SET status = ?, ended_at = ?, duration_seconds = ?, score = ?
            WHERE id = ?
            """,
            (status, ended_at, duration_seconds, score, game_id),
        )


def abandon_active_games(ended_at: str, durations: dict[str, int]) -> None:
    """Abandonne toutes les parties actives avec leurs durées connues."""
    with _connect() as db:
        rows = db.execute("SELECT id FROM games WHERE status = 'active'").fetchall()
        for row in rows:
            db.execute(
                """
                UPDATE games
                SET status = 'abandoned', ended_at = ?, duration_seconds = ?, score = 0
                WHERE id = ?
                """,
                (ended_at, durations.get(row["id"], 0), row["id"]),
            )


def list_history(limit: int = 50) -> list[Game]:
    """Liste les parties terminées de la plus récente à la plus ancienne."""
    with _connect() as db:
        rows = db.execute(
            "SELECT * FROM games WHERE status != 'active' ORDER BY started_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [_decode(row) for row in rows]


def set_player_name(game_id: str, player_name: str) -> None:
    """Associe un pseudonyme à une partie terminée."""
    with _connect() as db:
        cursor = db.execute(
            "UPDATE games SET player_name = ? WHERE id = ? AND status != 'active'",
            (player_name, game_id),
        )
    if cursor.rowcount == 0:
        raise ValueError("La partie doit être terminée avant de saisir un pseudonyme")


def get_stats() -> Stats:
    """Agrège les statistiques de toutes les parties terminées."""
    with _connect() as db:
        row = db.execute(
            """
            SELECT
                COUNT(*) AS games_total,
                SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) AS wins,
                COALESCE(SUM(score), 0) AS total_score,
                COALESCE(MAX(score), 0) AS best_score,
                COALESCE(AVG(CASE WHEN status = 'won' THEN duration_seconds END), 0) AS average_win_duration
            FROM games
            WHERE status != 'active'
            """
        ).fetchone()
    return {
        "games_total": int(row["games_total"] or 0),
        "wins": int(row["wins"] or 0),
        "total_score": int(row["total_score"] or 0),
        "best_score": int(row["best_score"] or 0),
        "average_win_duration": round(float(row["average_win_duration"] or 0), 1),
    }


def _decode(row: sqlite3.Row) -> Game:
    """Convertit une ligne SQLite en structure de partie typée."""
    mode = str(row["mode"])
    secret = cast(list[str], json.loads(row["secret_json"]))
    attempts = cast(list[Attempt], json.loads(row["attempts_json"]))
    if mode == "colors":
        secret = [LEGACY_COLOR_VALUES.get(value, value) for value in secret]
        for attempt in attempts:
            attempt["guess"] = [
                LEGACY_COLOR_VALUES.get(value, value) for value in attempt["guess"]
            ]
    row_keys = set(row.keys())
    code_length = int(row["code_length"] or 4) if "code_length" in row_keys else len(secret)
    return {
        "id": row["id"],
        "mode": mode,
        "code_length": code_length,
        "secret": secret,
        "attempts": attempts,
        "status": row["status"],
        "started_at": row["started_at"],
        "ended_at": row["ended_at"],
        "duration_seconds": int(row["duration_seconds"] or 0),
        "score": int(row["score"] or 0),
        "player_name": str(row["player_name"]) if row["player_name"] else None,
    }
