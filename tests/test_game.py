import pytest

from app.game import (
    CODE_LENGTH,
    MODES,
    calculate_score,
    compact_result,
    evaluate_guess,
    generate_secret,
    live_score,
    validate_guess,
)


def test_generate_secret_uses_selected_mode() -> None:
    """Le secret généré respecte la longueur et les choix du mode."""
    secret = generate_secret("digits")
    allowed = {choice["value"] for choice in MODES["digits"]["choices"]}

    assert len(secret) == CODE_LENGTH
    assert set(secret) <= allowed


def test_generate_secret_rejects_unknown_mode() -> None:
    """La génération refuse un mode inconnu."""
    with pytest.raises(ValueError, match="Mode de jeu inconnu"):
        generate_secret("letters")


def test_evaluate_guess_counts_well_and_misplaced() -> None:
    """L'évaluation distingue les valeurs bien et mal placées."""
    secret = ["red", "red", "blue", "green"]
    guess = ["red", "blue", "red", "yellow"]

    assert evaluate_guess(secret, guess) == (1, 2)
    assert compact_result(1, 2) == "12"


def test_evaluate_guess_handles_duplicates_without_double_counting() -> None:
    """L'évaluation ne compte pas deux fois les valeurs dupliquées."""
    secret = ["red", "red", "blue", "blue"]
    guess = ["red", "blue", "red", "blue"]

    assert evaluate_guess(secret, guess) == (2, 2)


def test_evaluate_guess_does_not_reuse_one_secret_value() -> None:
    """Une valeur du secret ne peut correspondre qu'à une proposition."""
    secret = ["red", "blue", "green", "yellow"]
    guess = ["red", "red", "red", "red"]

    assert evaluate_guess(secret, guess) == (1, 0)


def test_validate_guess_accepts_repeated_values() -> None:
    """La validation autorise les répétitions prévues par les règles."""
    validate_guess("digits", ["1", "1", "6", "6"])


def test_validate_guess_rejects_wrong_length() -> None:
    """La validation refuse une combinaison de mauvaise longueur."""
    with pytest.raises(ValueError):
        validate_guess("colors", ["red", "blue"])


def test_validate_guess_rejects_unknown_choice() -> None:
    """La validation refuse une valeur absente du mode."""
    with pytest.raises(ValueError):
        validate_guess("digits", ["1", "2", "3", "9"])


def test_score_rewards_fast_low_attempt_win() -> None:
    """Le score final récompense une victoire rapide en peu d'essais."""
    assert calculate_score(attempt_count=1, duration_seconds=20) == 980
    assert calculate_score(attempt_count=3, duration_seconds=20) == 780


def test_score_has_minimum_for_a_win() -> None:
    """Le score final d'une victoire ne descend jamais sous son minimum."""
    assert calculate_score(attempt_count=20, duration_seconds=5000) == 100


def test_live_score_applies_attempt_and_time_penalties() -> None:
    """Le score provisoire applique les pénalités et reste positif."""
    assert live_score(attempt_count=2, elapsed_seconds=30) == 770
    assert live_score(attempt_count=20, elapsed_seconds=5000) == 0


def test_score_ignores_negative_penalties() -> None:
    """Les compteurs négatifs ne créent pas de bonus artificiel."""
    assert calculate_score(attempt_count=-1, duration_seconds=-5) == 1000
    assert live_score(attempt_count=-1, elapsed_seconds=-5) == 1000
