from fastapi.testclient import TestClient

from app import storage
from app.main import app


def use_test_database(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "mastermind-test.db")
    storage.init_db()


def test_game_flow_persists_win_and_stats(tmp_path, monkeypatch) -> None:
    use_test_database(tmp_path, monkeypatch)

    with TestClient(app) as client:
        response = client.post("/api/games", json={"mode": "digits"})
        assert response.status_code == 201
        game = response.json()
        assert game["mode"] == "digits"
        assert game["status"] == "active"
        assert game["secret"] is None

        secret = storage.get_game(game["id"])["secret"]
        response = client.post(
            f"/api/games/{game['id']}/guesses",
            json={"guess": secret},
        )
        assert response.status_code == 200
        finished = response.json()
        assert finished["status"] == "won"
        assert finished["attempts"][0]["result"] == "40"
        assert finished["secret"] == secret
        assert finished["score"] > 0

        stats = client.get("/api/stats").json()
        assert stats["games_total"] == 1
        assert stats["wins"] == 1
        assert stats["total_score"] == finished["score"]

        history = client.get("/api/history").json()
        assert len(history) == 1
        assert history[0]["id"] == game["id"]


def test_starting_another_mode_abandons_current_game(tmp_path, monkeypatch) -> None:
    use_test_database(tmp_path, monkeypatch)

    with TestClient(app) as client:
        colors = client.post("/api/games", json={"mode": "colors"}).json()
        digits = client.post("/api/games", json={"mode": "digits"}).json()

        assert digits["mode"] == "digits"
        assert digits["status"] == "active"

        old_game = storage.get_game(colors["id"])
        assert old_game["status"] == "abandoned"

        history = client.get("/api/history").json()
        assert history[0]["id"] == colors["id"]
        assert history[0]["status"] == "abandoned"


def test_invalid_guess_is_rejected(tmp_path, monkeypatch) -> None:
    use_test_database(tmp_path, monkeypatch)

    with TestClient(app) as client:
        game = client.post("/api/games", json={"mode": "digits"}).json()
        response = client.post(
            f"/api/games/{game['id']}/guesses",
            json={"guess": ["1", "2", "3", "9"]},
        )

        assert response.status_code == 400
