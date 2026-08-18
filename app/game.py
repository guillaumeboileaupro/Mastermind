from collections import Counter
from random import SystemRandom

from .types import FeedbackStatus, ModeDefinition

CODE_LENGTH = 4

LEGACY_COLOR_VALUES: dict[str, str] = {
    "red": "#ef4444",
    "blue": "#3b82f6",
    "green": "#22c55e",
    "yellow": "#eab308",
    "purple": "#a855f7",
    "orange": "#f97316",
}

MODES: dict[str, ModeDefinition] = {
    "colors": {
        "label": "Couleurs",
        "choices": [
            {"value": "#ef4444", "label": "Rouge"},
            {"value": "#3b82f6", "label": "Bleu"},
            {"value": "#22c55e", "label": "Vert"},
            {"value": "#eab308", "label": "Jaune"},
            {"value": "#a855f7", "label": "Violet"},
            {"value": "#f97316", "label": "Orange"},
        ],
    },
    "digits": {
        "label": "Chiffres",
        "choices": [
            {"value": str(value), "label": str(value)} for value in range(1, 7)
        ],
    },
}

_rng = SystemRandom()


def generate_secret(mode: str) -> list[str]:
    """Génère un code secret aléatoire pour le mode demandé."""
    if mode not in MODES:
        raise ValueError("Mode de jeu inconnu")
    values = [choice["value"] for choice in MODES[mode]["choices"]]
    return [_rng.choice(values) for _ in range(CODE_LENGTH)]


def validate_guess(mode: str, guess: list[str]) -> None:
    """Vérifie qu'une proposition respecte le mode et la longueur du code."""
    if mode not in MODES:
        raise ValueError("Mode de jeu inconnu")
    if len(guess) != CODE_LENGTH:
        raise ValueError(f"La combinaison doit contenir {CODE_LENGTH} valeurs")
    allowed = {choice["value"] for choice in MODES[mode]["choices"]}
    if any(value not in allowed for value in guess):
        raise ValueError("La combinaison contient une valeur invalide")


def evaluate_guess_feedback(secret: list[str], guess: list[str]) -> list[FeedbackStatus]:
    """Retourne l'état de chaque position sans compter deux fois les doublons."""
    feedback: list[FeedbackStatus] = ["absent"] * len(guess)
    remaining_secret: Counter[str] = Counter()

    for index, (expected, actual) in enumerate(zip(secret, guess)):
        if expected == actual:
            feedback[index] = "well_placed"
        else:
            remaining_secret[expected] += 1

    for index, actual in enumerate(guess):
        if feedback[index] == "well_placed":
            continue
        if remaining_secret[actual] > 0:
            feedback[index] = "misplaced"
            remaining_secret[actual] -= 1

    return feedback


def evaluate_guess(secret: list[str], guess: list[str]) -> tuple[int, int]:
    """Compte les valeurs bien placées et mal placées d'une proposition."""
    feedback = evaluate_guess_feedback(secret, guess)
    return feedback.count("well_placed"), feedback.count("misplaced")


def compact_result(well_placed: int, misplaced: int) -> str:
    """Encode les deux compteurs du résultat sous une forme compacte."""
    return f"{well_placed}{misplaced}"


def calculate_score(attempt_count: int, duration_seconds: int) -> int:
    """Calcule le score final d'une partie gagnée."""
    # 1000 points pour une victoire immédiate, puis pénalité par essai et seconde.
    penalty = max(0, attempt_count - 1) * 100 + max(0, duration_seconds)
    return max(100, 1000 - penalty)


def live_score(attempt_count: int, elapsed_seconds: int) -> int:
    """Calcule le score provisoire affiché pendant une partie."""
    penalty = max(0, attempt_count) * 100 + max(0, elapsed_seconds)
    return max(0, 1000 - penalty)
