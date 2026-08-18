import pytest

from app.game import (
    CODE_LENGTH,
    MODES,
    calculate_score,
    compact_result,
    evaluate_guess,
    evaluate_guess_feedback,
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


def test_color_mode_uses_hex_values_directly() -> None:
    """Les couleurs utilisent leur code hexadécimal comme valeur de jeu."""
    choices = MODES["colors"]["choices"]

    assert all(choice["value"].startswith("#") for choice in choices)
    assert all(set(choice) == {"value", "label"} for choice in choices)


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


def test_easy_feedback_identifies_each_position() -> None:
    """Le mode facile peut expliquer chaque pion de la tentative."""
    secret = ["red", "red", "blue", "green"]
    guess = ["red", "blue", "red", "yellow"]

    assert evaluate_guess_feedback(secret, guess) == [
        "well_placed",
        "misplaced",
        "misplaced",
        "absent",
    ]


def test_easy_feedback_handles_duplicates_without_false_hint() -> None:
    """Un doublon en trop est indiqué absent plutôt que mal placé."""
    secret = ["red", "blue", "green", "yellow"]
    guess = ["red", "red", "red", "red"]

    assert evaluate_guess_feedback(secret, guess) == [
        "well_placed",
        "absent",
        "absent",
        "absent",
    ]


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


def test_validate_guess_accepts_hex_colors() -> None:
    """La validation accepte directement les codes des couleurs disponibles."""
    validate_guess("colors", ["#ef4444", "#ef4444", "#3b82f6", "#22c55e"])


def test_validate_guess_rejects_wrong_length() -> None:
    """La validation refuse une combinaison de mauvaise longueur."""
    with pytest.raises(ValueError):
        validate_guess("colors", ["#ef4444", "#3b82f6"])


def test_validate_guess_rejects_unknown_choice() -> None:
    """La validation refuse une valeur absente du mode."""
    with pytest.raises(ValueError):
        validate_guess("digits", ["1", "2", "3", "9"])


def test_score_rewards_low_attempt_win() -> None:
    """Le score final dépend uniquement du nombre d'essais."""
    assert calculate_score(attempt_count=1) == 1000
    assert calculate_score(attempt_count=3) == 800


def test_score_is_zero_outside_win_limit() -> None:
    """Une combinaison trouvée après neuf essais ne rapporte aucun point."""
    assert calculate_score(attempt_count=9) == 200
    assert calculate_score(attempt_count=10) == 100
    assert calculate_score(attempt_count=11) == 0


def test_live_score_ignores_elapsed_time() -> None:
    """Le score provisoire applique uniquement la pénalité des essais."""
    assert live_score(attempt_count=2) == 800
    assert live_score(attempt_count=20) == 0


def test_score_ignores_negative_penalties() -> None:
    """Les compteurs négatifs ne créent pas de bonus artificiel."""
    assert calculate_score(attempt_count=-1) == 1000
    assert live_score(attempt_count=-1) == 1000
