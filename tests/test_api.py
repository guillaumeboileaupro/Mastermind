from pathlib import Path
from typing import cast

import pytest
from fastapi.testclient import TestClient

from app import storage
from app.main import app
from app.types import PublicGame, Stats


def use_test_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Configure une base SQLite isolée pour un test d'API."""
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "mastermind-test.db")
    storage.init_db()


def test_game_flow_persists_win_and_stats(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Une victoire est persistée et intégrée aux statistiques."""
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
        assert finished["attempts"][0]["feedback"] == ["well_placed"] * 4
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
    """Démarrer un autre mode abandonne la partie active."""
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
    """Une proposition contenant une valeur inconnue est refusée."""
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


def test_information_endpoints_and_empty_current_game(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Les routes d'accueil, santé, modes et partie courante répondent."""
    use_test_database(tmp_path, monkeypatch)

    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        assert client.get("/api/health").json() == {"status": "ok"}
        modes = client.get("/api/modes").json()
        assert modes["code_length"] == 4
        assert set(modes["modes"]) == {"colors", "digits"}
        assert client.get("/api/games/current").json() is None


def test_new_game_rejects_unknown_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """La création d'une partie refuse un mode inconnu."""
    use_test_database(tmp_path, monkeypatch)

    with TestClient(app) as client:
        response = client.post("/api/games", json={"mode": "letters"})

    assert response.status_code == 400


def test_give_up_finishes_active_game(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """L'abandon termine la partie et la rend visible dans l'historique."""
    use_test_database(tmp_path, monkeypatch)

    with TestClient(app) as client:
        game = cast(
            PublicGame,
            client.post("/api/games", json={"mode": "digits"}).json(),
        )
        response = client.post(f"/api/games/{game['id']}/give-up")
        abandoned = cast(PublicGame, response.json())

        assert response.status_code == 200
        assert abandoned["status"] == "lost"
        assert abandoned["secret"] is not None
        assert client.post(f"/api/games/{game['id']}/give-up").status_code == 409


def test_missing_games_return_not_found(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Les actions sur une partie inexistante retournent une erreur 404."""
    use_test_database(tmp_path, monkeypatch)

    with TestClient(app) as client:
        guess = client.post(
            "/api/games/missing/guesses",
            json={"guess": ["1", "2", "3", "4"]},
        )
        give_up = client.post("/api/games/missing/give-up")

    assert guess.status_code == 404
    assert give_up.status_code == 404
