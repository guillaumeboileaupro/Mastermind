from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .game import (
    CODE_LENGTH,
    MODES,
    calculate_score,
    compact_result,
    evaluate_guess,
    generate_secret,
    live_score,
    validate_guess,
)
from .storage import (
    abandon_active_games,
    create_game,
    finish_game,
    get_current_game,
    get_game,
    get_stats,
    init_db,
    list_history,
    save_attempts,
)
from .types import Attempt, Game, ModesResponse, PublicGame, Stats

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def elapsed_seconds(game: Game, now: datetime | None = None) -> int:
    if game["status"] != "active":
        return int(game["duration_seconds"])
    current = now or utc_now()
    started = parse_datetime(game["started_at"])
    return max(0, int((current - started).total_seconds()))


def public_game(game: Game) -> PublicGame:
    elapsed = elapsed_seconds(game)
    active = game["status"] == "active"
    return {
        "id": game["id"],
        "mode": game["mode"],
        "status": game["status"],
        "attempts": game["attempts"],
        "started_at": game["started_at"],
        "ended_at": game["ended_at"],
        "elapsed_seconds": elapsed,
        "score": game["score"],
        "current_score": live_score(len(game["attempts"]), elapsed) if active else game["score"],
        "secret": None if active else game["secret"],
    }


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title="Mastermind API", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class NewGameRequest(BaseModel):
    mode: str


class GuessRequest(BaseModel):
    guess: list[str]


@app.get("/")
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/modes")
def modes() -> ModesResponse:
    return {
        "code_length": CODE_LENGTH,
        "repetition_allowed": True,
        "modes": MODES,
    }


@app.get("/api/games/current")
def current_game() -> PublicGame | None:
    game = get_current_game()
    return public_game(game) if game else None


@app.post("/api/games", status_code=201)
def new_game(payload: NewGameRequest) -> PublicGame:
    if payload.mode not in MODES:
        raise HTTPException(status_code=400, detail="Mode de jeu inconnu")

    now = utc_now()
    current = get_current_game()
    if current:
        abandon_active_games(
            now.isoformat(),
            {current["id"]: elapsed_seconds(current, now)},
        )

    game = create_game(payload.mode, generate_secret(payload.mode), now.isoformat())
    return public_game(game)


@app.post("/api/games/{game_id}/guesses")
def submit_guess(game_id: str, payload: GuessRequest) -> PublicGame:
    game = get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Partie introuvable")
    if game["status"] != "active":
        raise HTTPException(status_code=409, detail="Cette partie est terminée")

    try:
        validate_guess(game["mode"], payload.guess)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    well_placed, misplaced = evaluate_guess(game["secret"], payload.guess)
    attempts: list[Attempt] = list(game["attempts"])
    now = utc_now()
    attempts.append(
        {
            "number": len(attempts) + 1,
            "guess": payload.guess,
            "well_placed": well_placed,
            "misplaced": misplaced,
            "result": compact_result(well_placed, misplaced),
            "created_at": now.isoformat(),
        }
    )
    save_attempts(game_id, attempts)

    if well_placed == CODE_LENGTH:
        duration = elapsed_seconds(game, now)
        score = calculate_score(len(attempts), duration)
        finish_game(
            game_id,
            status="won",
            ended_at=now.isoformat(),
            duration_seconds=duration,
            score=score,
        )

    updated = get_game(game_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Partie introuvable")
    return public_game(updated)


@app.post("/api/games/{game_id}/give-up")
def give_up(game_id: str) -> PublicGame:
    game = get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Partie introuvable")
    if game["status"] != "active":
        raise HTTPException(status_code=409, detail="Cette partie est déjà terminée")

    now = utc_now()
    finish_game(
        game_id,
        status="lost",
        ended_at=now.isoformat(),
        duration_seconds=elapsed_seconds(game, now),
        score=0,
    )
    updated = get_game(game_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Partie introuvable")
    return public_game(updated)


@app.get("/api/history")
def history(limit: int = Query(default=50, ge=1, le=200)) -> list[PublicGame]:
    return [public_game(game) for game in list_history(limit)]


@app.get("/api/stats")
def stats() -> Stats:
    return get_stats()
