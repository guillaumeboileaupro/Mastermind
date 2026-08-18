import pytest

from app.game import calculate_score, compact_result, evaluate_guess, validate_guess


def test_evaluate_guess_counts_well_and_misplaced() -> None:
    secret = ["red", "red", "blue", "green"]
    guess = ["red", "blue", "red", "yellow"]

    assert evaluate_guess(secret, guess) == (1, 2)
    assert compact_result(1, 2) == "12"


def test_evaluate_guess_handles_duplicates_without_double_counting() -> None:
    secret = ["red", "red", "blue", "blue"]
    guess = ["red", "blue", "red", "blue"]

    assert evaluate_guess(secret, guess) == (2, 2)


def test_evaluate_guess_does_not_reuse_one_secret_value() -> None:
    secret = ["red", "blue", "green", "yellow"]
    guess = ["red", "red", "red", "red"]

    assert evaluate_guess(secret, guess) == (1, 0)


def test_validate_guess_accepts_repeated_values() -> None:
    validate_guess("digits", ["1", "1", "6", "6"])


def test_validate_guess_rejects_wrong_length() -> None:
    with pytest.raises(ValueError):
        validate_guess("colors", ["red", "blue"])


def test_validate_guess_rejects_unknown_choice() -> None:
    with pytest.raises(ValueError):
        validate_guess("digits", ["1", "2", "3", "9"])


def test_score_rewards_fast_low_attempt_win() -> None:
    assert calculate_score(attempt_count=1, duration_seconds=20) == 980
    assert calculate_score(attempt_count=3, duration_seconds=20) == 780


def test_score_has_minimum_for_a_win() -> None:
    assert calculate_score(attempt_count=20, duration_seconds=5000) == 100
