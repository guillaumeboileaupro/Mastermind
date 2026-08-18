from typing_extensions import NotRequired, TypedDict


class Attempt(TypedDict):
    number: int
    guess: list[str]
    well_placed: int
    misplaced: int
    result: str
    created_at: str


class Game(TypedDict):
    id: str
    mode: str
    secret: list[str]
    attempts: list[Attempt]
    status: str
    started_at: str
    ended_at: str | None
    duration_seconds: int
    score: int


class PublicGame(TypedDict):
    id: str
    mode: str
    status: str
    attempts: list[Attempt]
    started_at: str
    ended_at: str | None
    elapsed_seconds: int
    score: int
    current_score: int
    secret: list[str] | None


class Choice(TypedDict):
    value: str
    label: str
    color: NotRequired[str]


class ModeDefinition(TypedDict):
    label: str
    choices: list[Choice]


class ModesResponse(TypedDict):
    code_length: int
    repetition_allowed: bool
    modes: dict[str, ModeDefinition]


class Stats(TypedDict):
    games_total: int
    wins: int
    total_score: int
    best_score: int
    average_win_duration: float
