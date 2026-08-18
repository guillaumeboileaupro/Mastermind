from datetime import datetime, timezone

from app.main import elapsed_seconds, parse_datetime, public_game, utc_now
from app.types import Game


def active_game() -> Game:
    """Construit une partie active minimale pour les tests de présentation."""
    return {
        "id": "game-id",
        "mode": "digits",
        "secret": ["1", "2", "3", "4"],
        "attempts": [],
        "status": "active",
        "started_at": "2026-01-01T00:00:00+00:00",
        "ended_at": None,
        "duration_seconds": 0,
        "score": 0,
    }


def test_utc_now_returns_aware_utc_datetime() -> None:
    """L'horloge applicative retourne toujours une date UTC consciente."""
    now = utc_now()

    assert now.tzinfo == timezone.utc


def test_parse_datetime_reads_iso_value() -> None:
    """Une date ISO 8601 est convertie sans perdre son fuseau."""
    parsed = parse_datetime("2026-01-01T12:30:00+00:00")

    assert parsed == datetime(2026, 1, 1, 12, 30, tzinfo=timezone.utc)


def test_elapsed_seconds_uses_clock_for_active_game() -> None:
    """La durée d'une partie active est calculée depuis son démarrage."""
    now = datetime(2026, 1, 1, 0, 0, 12, tzinfo=timezone.utc)

    assert elapsed_seconds(active_game(), now) == 12


def test_elapsed_seconds_uses_stored_duration_for_finished_game() -> None:
    """La durée persistée d'une partie terminée ne continue pas à évoluer."""
    game = active_game()
    game["status"] = "won"
    game["duration_seconds"] = 9

    assert elapsed_seconds(game) == 9


def test_public_game_hides_active_secret_and_exposes_finished_secret() -> None:
    """La représentation publique ne révèle le secret qu'après la fin."""
    game = active_game()
    active = public_game(game)
    game["status"] = "won"
    game["score"] = 900
    finished = public_game(game)

    assert active["secret"] is None
    assert active["current_score"] <= 1000
    assert finished["secret"] == ["1", "2", "3", "4"]
    assert finished["current_score"] == 900
