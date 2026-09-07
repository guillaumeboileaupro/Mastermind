from collections import Counter
from random import SystemRandom

from .types import Choice, FeedbackStatus, ModeDefinition
from .variants import VARIANTS, get_variant, max_attempts_for

CODE_LENGTH = 4
MAX_WIN_ATTEMPTS = 10
MAX_SCORE = 1000

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


def _choices(mode: str) -> list[Choice]:
    if mode in MODES:
        return MODES[mode]["choices"]
    variant = get_variant(mode)
    if variant:
        return variant["choices"]
    raise ValueError("Mode de jeu inconnu")


def allowed_code_lengths(mode: str) -> list[int]:
    """Retourne les longueurs autorisées pour un mode ou une variante."""
    if mode in MODES:
        return [CODE_LENGTH]
    variant = get_variant(mode)
    if variant:
        return variant["code_lengths"]
    raise ValueError("Mode de jeu inconnu")


def default_code_length(mode: str) -> int:
    """Retourne la longueur par défaut d'un mode ou d'une variante."""
    if mode in MODES:
        return CODE_LENGTH
    variant = get_variant(mode)
    if variant:
        return variant["default_code_length"]
    raise ValueError("Mode de jeu inconnu")


def generate_secret(mode: str, code_length: int | None = None) -> list[str]:
    """Génère un code secret aléatoire pour le mode ou la variante demandé."""
    values = [choice["value"] for choice in _choices(mode)]
    length = code_length if code_length is not None else default_code_length(mode)
    if length not in allowed_code_lengths(mode):
        raise ValueError("Longueur de code invalide pour cette variante")
    return [_rng.choice(values) for _ in range(length)]


def validate_guess(mode: str, guess: list[str], code_length: int | None = None) -> None:
    """Vérifie qu'une proposition respecte les choix et la longueur du jeu."""
    length = code_length if code_length is not None else default_code_length(mode)
    if length not in allowed_code_lengths(mode):
        raise ValueError("Longueur de code invalide pour cette variante")
    if len(guess) != length:
        raise ValueError(f"La combinaison doit contenir {length} valeurs")
    allowed = {choice["value"] for choice in _choices(mode)}
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


def evaluate_variant_feedback(
    mode: str,
    secret: list[str],
    guess: list[str],
) -> list[FeedbackStatus]:
    """Applique le retour propre à la variante quand elle en définit un."""
    variant = get_variant(mode)
    if variant and variant.get("feedback_kind") == "alphabet":
        feedback: list[FeedbackStatus] = []
        for expected, actual in zip(secret, guess):
            if expected == actual:
                feedback.append("well_placed")
            elif expected > actual:
                feedback.append("higher")
            else:
                feedback.append("lower")
        return feedback
    return evaluate_guess_feedback(secret, guess)


def evaluate_guess(secret: list[str], guess: list[str]) -> tuple[int, int]:
    """Compte les valeurs bien placées et mal placées d'une proposition."""
    feedback = evaluate_guess_feedback(secret, guess)
    return feedback.count("well_placed"), feedback.count("misplaced")


def compact_result(well_placed: int, misplaced: int) -> str:
    """Encode les deux compteurs du résultat sous une forme compacte."""
    return f"{well_placed}{misplaced}"


def calculate_score(
    attempt_count: int,
    max_attempts: int = MAX_WIN_ATTEMPTS,
    duration_seconds: int = 0,
) -> int:
    """Calcule le score d'une partie selon les essais et sa durée."""
    attempt_score = (max_attempts + 1 - max(1, attempt_count)) * 100
    return max(0, attempt_score - max(0, duration_seconds))


def live_score(
    attempt_count: int,
    max_attempts: int = MAX_WIN_ATTEMPTS,
    elapsed_seconds: int = 0,
) -> int:
    """Calcule le score disponible selon les essais et le temps écoulé."""
    attempt_score = max_attempts * 100 - max(0, attempt_count) * 100
    return max(0, attempt_score - max(0, elapsed_seconds))


__all__ = [
    "CODE_LENGTH",
    "MAX_WIN_ATTEMPTS",
    "MAX_SCORE",
    "LEGACY_COLOR_VALUES",
    "MODES",
    "VARIANTS",
    "allowed_code_lengths",
    "calculate_score",
    "compact_result",
    "default_code_length",
    "evaluate_guess",
    "evaluate_guess_feedback",
    "evaluate_variant_feedback",
    "generate_secret",
    "live_score",
    "max_attempts_for",
    "validate_guess",
]
