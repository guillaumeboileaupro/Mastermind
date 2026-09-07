from pathlib import Path
from typing import cast

import pytest
from fastapi.testclient import TestClient

from app import storage
from app.game import evaluate_variant_feedback, generate_secret
from app.main import app
from app.types import PublicGame
from app.variants import VARIANTS


def use_test_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "mastermind-variants.db")
    storage.init_db()


def test_catalog_contains_wikipedia_table_and_super_code() -> None:
    assert len(VARIANTS) == 21
    assert "mastermind-1972" in VARIANTS
    assert "bagels-1972" in VARIANTS
    assert "royale-mastermind-1972" in VARIANTS
    assert "super-mastermind-1972" in VARIANTS
    assert "secret-search-1997" in VARIANTS
    assert "mini-mastermind-2004" in VARIANTS
    assert "super-code" in VARIANTS


def test_every_variant_generates_a_valid_default_secret() -> None:
    for key, variant in VARIANTS.items():
        secret = generate_secret(key)
        allowed = {choice["value"] for choice in variant["choices"]}
        assert len(secret) == variant["default_code_length"]
        assert set(secret) <= allowed


def test_electronic_variants_expose_their_multiple_lengths() -> None:
    assert VARIANTS["electronic-mastermind-1977"]["code_lengths"] == [3, 4, 5]
    assert VARIANTS["super-sonic-1979"]["code_lengths"] == [3, 4, 5, 6]
    assert VARIANTS["secret-search-1997"]["code_lengths"] == [3, 4, 5, 6]


def test_secret_search_uses_alphabet_direction_feedback() -> None:
    feedback = evaluate_variant_feedback(
        "secret-search-1997",
        ["C", "B", "D"],
        ["A", "B", "F"],
    )
    assert feedback == ["higher", "well_placed", "lower"]


def test_api_starts_selected_variant_with_selected_length(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    use_test_database(tmp_path, monkeypatch)
    with TestClient(app) as client:
        response = client.post(
            "/api/games",
            json={"mode": "electronic-mastermind-1977", "code_length": 5},
        )
        assert response.status_code == 201
        game = cast(PublicGame, response.json())
        stored = storage.get_game(game["id"])

    assert game["code_length"] == 5
    assert game["max_attempts"] == 10
    assert stored is not None
    assert len(stored["secret"]) == 5


def test_api_rejects_length_not_supported_by_variant(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    use_test_database(tmp_path, monkeypatch)
    with TestClient(app) as client:
        response = client.post(
            "/api/games",
            json={"mode": "electronic-mastermind-1977", "code_length": 6},
        )
    assert response.status_code == 400


def test_mini_mastermind_1976_uses_six_scoring_attempts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    use_test_database(tmp_path, monkeypatch)
    with TestClient(app) as client:
        game = cast(
            PublicGame,
            client.post("/api/games", json={"mode": "mini-mastermind-1976"}).json(),
        )
        stored = storage.get_game(game["id"])
        assert stored is not None
        secret = stored["secret"]
        values = [choice["value"] for choice in VARIANTS["mini-mastermind-1976"]["choices"]]
        wrong = [next(candidate for candidate in values if candidate != value) for value in secret]

        for _ in range(6):
            response = client.post(
                f"/api/games/{game['id']}/guesses",
                json={"guess": wrong},
            )
            assert response.status_code == 200
            assert response.json()["status"] == "active"

        finished = client.post(
            f"/api/games/{game['id']}/guesses",
            json={"guess": secret},
        ).json()

    assert game["max_attempts"] == 6
    assert finished["status"] == "completed"
    assert finished["score"] == 0


def test_modes_endpoint_exposes_variant_catalog(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    use_test_database(tmp_path, monkeypatch)
    with TestClient(app) as client:
        payload = client.get("/api/modes").json()

    assert set(payload["modes"]) == {"colors", "digits"}
    assert set(payload["variants"]) == set(VARIANTS)
    assert payload["variants"]["mastermind-kids-1996"]["default_code_length"] == 3
