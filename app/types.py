from typing import Literal

from typing_extensions import NotRequired, TypedDict

FeedbackStatus = Literal[
    "well_placed",
    "misplaced",
    "absent",
    "higher",
    "lower",
]


class Attempt(TypedDict):
    number: int
    guess: list[str]
    well_placed: int
    misplaced: int
    result: str
    feedback: NotRequired[list[FeedbackStatus]]
    created_at: str


class Game(TypedDict):
    id: str
    mode: str
    code_length: int
    secret: list[str]
    attempts: list[Attempt]
    status: str
    started_at: str
    ended_at: str | None
    duration_seconds: int
    score: int
    player_name: str | None


class PublicGame(TypedDict):
    id: str
    mode: str
    code_length: int
    max_attempts: int
    status: str
    attempts: list[Attempt]
    started_at: str
    ended_at: str | None
    elapsed_seconds: int
    score: int
    current_score: int
    secret: list[str] | None
    player_name: str | None


class Choice(TypedDict):
    value: str
    label: str
    color: NotRequired[str]
    symbol: NotRequired[str]


class ModeDefinition(TypedDict):
    label: str
    choices: list[Choice]


class VariantDefinition(TypedDict):
    label: str
    year: str
    choices: list[Choice]
    code_lengths: list[int]
    default_code_length: int
    max_attempts: int
    description: str
    note: str
    rules: NotRequired[list[str]]
    feedback_kind: NotRequired[str]


class ModesResponse(TypedDict):
    code_length: int
    repetition_allowed: bool
    modes: dict[str, ModeDefinition]
    variants: dict[str, VariantDefinition]


class Stats(TypedDict):
    games_total: int
    wins: int
    best_score: int
    average_win_duration: float
