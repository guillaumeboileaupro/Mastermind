from pathlib import Path

import pytest

from app import storage
from app.types import Attempt


def configure_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Configure et initialise une base temporaire pour un test de stockage."""
    database = tmp_path / "mastermind-storage-test.db"
    monkeypatch.setattr(storage, "DB_PATH", database)
    storage.init_db()
    return database


def test_default_db_path_uses_xdg_data_home(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Le chemin par défaut respecte la variable XDG_DATA_HOME."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    assert storage._default_db_path() == tmp_path / "mastermind" / "mastermind.db"


def test_init_and_connect_create_typed_sqlite_rows(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """L'initialisation crée le fichier et configure les lignes nommées."""
    database = configure_database(tmp_path, monkeypatch)

    with storage._connect() as connection:
        row = connection.execute("SELECT 1 AS value").fetchone()

    assert database.exists()
    assert row["value"] == 1


def test_game_storage_lifecycle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Une partie et ses tentatives suivent tout leur cycle persistant."""
    configure_database(tmp_path, monkeypatch)
    game = storage.create_game("digits", ["1", "2", "3", "4"], "2026-01-01T00:00:00+00:00")
    attempt: Attempt = {
        "number": 1,
        "guess": ["1", "2", "4", "3"],
        "well_placed": 2,
        "misplaced": 2,
        "result": "22",
        "created_at": "2026-01-01T00:00:05+00:00",
    }

    assert storage.get_current_game() == game
    storage.save_attempts(game["id"], [attempt])
    storage.finish_game(
        game["id"],
        status="won",
        ended_at="2026-01-01T00:00:05+00:00",
        duration_seconds=5,
        score=995,
    )

    finished = storage.get_game(game["id"])
    assert finished is not None
    assert finished["attempts"] == [attempt]
    assert finished["duration_seconds"] == 5
    assert storage.get_current_game() is None
    assert storage.list_history() == [finished]
    assert storage.list_history(limit=0) == []
    assert storage.get_stats() == {
        "games_total": 1,
        "wins": 1,
        "total_score": 995,
        "best_score": 995,
        "average_win_duration": 5.0,
    }


def test_abandon_active_games_uses_known_and_default_durations(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """L'abandon multiple applique une durée connue ou zéro par défaut."""
    configure_database(tmp_path, monkeypatch)
    first = storage.create_game("digits", ["1"] * 4, "2026-01-01T00:00:00+00:00")
    second = storage.create_game("colors", ["red"] * 4, "2026-01-01T00:00:01+00:00")

    storage.abandon_active_games("2026-01-01T00:00:10+00:00", {first["id"]: 10})

    abandoned_first = storage.get_game(first["id"])
    abandoned_second = storage.get_game(second["id"])
    assert abandoned_first is not None
    assert abandoned_second is not None
    assert abandoned_first["duration_seconds"] == 10
    assert abandoned_second["duration_seconds"] == 0
    assert abandoned_first["status"] == abandoned_second["status"] == "abandoned"


def test_get_game_returns_none_for_unknown_identifier(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """La lecture d'un identifiant absent retourne None."""
    configure_database(tmp_path, monkeypatch)

    assert storage.get_game("missing") is None
    assert storage.get_stats()["games_total"] == 0


def test_legacy_color_names_are_decoded_as_hex_values(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Les anciennes parties en noms de couleurs restent lisibles en hexadécimal."""
    configure_database(tmp_path, monkeypatch)
    game = storage.create_game(
        "colors",
        ["red", "blue", "green", "yellow"],
        "2026-01-01T00:00:00+00:00",
    )

    assert game["secret"] == ["#ef4444", "#3b82f6", "#22c55e", "#eab308"]
