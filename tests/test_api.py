from pathlib import Path
from typing import cast

import pytest
from fastapi.testclient import TestClient

from app import storage
from app.main import app
from app.types import PublicGame, Stats


def use_test_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "mastermind-test.db")
    storage.init_db()


def test_game_flow_persists_win_and_stats(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    use_test_database(tmp_path, monkeypatch)

    with TestClient(app) as client:
        response = client.post("/api/games", json={"mode": "digits"})
        assert response.status_code == 201
        game = cast(PublicGame, response.json())
        assert game["mode"] == "digits"
        assert game["status"] == "active"
        assert game["secret"] is None

        stored_game = storage.get_game(game["id"])
        assert stored_game is not None
        secret = stored_game["secret"]
        response = client.post(
            f"/api/games/{game['id']}/guesses",
            json={"guess": secret},
        )
        assert response.status_code == 200
        finished = cast(PublicGame, response.json())
        assert finished["status"] == "won"
        assert finished["attempts"][0]["result"] == "40"
        assert finished["secret"] == secret
        assert finished["score"] > 0

        stats = cast(Stats, client.get("/api/stats").json())
        assert stats["games_total"] == 1
        assert stats["wins"] == 1
        assert stats["total_score"] == finished["score"]

        history = cast(list[PublicGame], client.get("/api/history").json())
        assert len(history) == 1
        assert history[0]["id"] == game["id"]


def test_starting_another_mode_abandons_current_game(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    use_test_database(tmp_path, monkeypatch)

    with TestClient(app) as client:
        colors = cast(
            PublicGame,
            client.post("/api/games", json={"mode": "colors"}).json(),
        )
        digits = cast(
            PublicGame,
            client.post("/api/games", json={"mode": "digits"}).json(),
        )

        assert digits["mode"] == "digits"
        assert digits["status"] == "active"

        old_game = storage.get_game(colors["id"])
        assert old_game is not None
        assert old_game["status"] == "abandoned"

        history = cast(list[PublicGame], client.get("/api/history").json())
        assert history[0]["id"] == colors["id"]
        assert history[0]["status"] == "abandoned"


def test_invalid_guess_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    use_test_database(tmp_path, monkeypatch)

    with TestClient(app) as client:
        game = cast(
            PublicGame,
            client.post("/api/games", json={"mode": "digits"}).json(),
        )
        response = client.post(
            f"/api/games/{game['id']}/guesses",
            json={"guess": ["1", "2", "3", "9"]},
        )

        assert response.status_code == 400
