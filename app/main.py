from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .game import (
    CODE_LENGTH,
    MODES,
    VARIANTS,
    allowed_code_lengths,
    calculate_score,
    compact_result,
    default_code_length,
    evaluate_variant_feedback,
    generate_secret,
    live_score,
    max_attempts_for,
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
    reset_scores,
    save_attempts,
    set_player_name,
)
from .types import Attempt, Game, ModesResponse, PublicGame, Stats

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"


def utc_now() -> datetime:
    """Retourne l'instant courant avec le fuseau UTC."""
    return datetime.now(timezone.utc)


def parse_datetime(value: str) -> datetime:
    """Convertit une date ISO 8601 en objet datetime."""
    return datetime.fromisoformat(value)


def elapsed_seconds(game: Game, now: datetime | None = None) -> int:
    """Retourne la durée figée ou écoulée d'une partie."""
    if game["status"] != "active":
        return int(game["duration_seconds"])
    current = now or utc_now()
    started = parse_datetime(game["started_at"])
    return max(0, int((current - started).total_seconds()))


def public_game(game: Game) -> PublicGame:
    """Masque le secret actif et prépare une partie pour l'API publique."""
    elapsed = elapsed_seconds(game)
    active = game["status"] == "active"
    max_attempts = max_attempts_for(game["mode"])
    return {
        "id": game["id"],
        "mode": game["mode"],
        "code_length": game["code_length"],
        "max_attempts": max_attempts,
        "status": game["status"],
        "attempts": game["attempts"],
        "started_at": game["started_at"],
        "ended_at": game["ended_at"],
        "elapsed_seconds": elapsed,
        "score": game["score"],
        "current_score": (
            live_score(len(game["attempts"]), max_attempts, elapsed)
            if active
            else game["score"]
        ),
        "secret": None if active else game["secret"],
        "player_name": game["player_name"],
    }


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialise le stockage pendant le cycle de vie de l'application."""
    init_db()
    yield


app = FastAPI(title="Mastermind API", version="1.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class NewGameRequest(BaseModel):
    mode: str
    code_length: int | None = None


class GuessRequest(BaseModel):
    guess: list[str]


class PlayerNameRequest(BaseModel):
    player_name: str


@app.get("/")
def home() -> FileResponse:
    """Sert la page principale de l'application."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    """Indique que le service HTTP est disponible."""
    return {"status": "ok"}


@app.get("/api/modes")
def modes() -> ModesResponse:
    """Expose les anciens modes et le catalogue des variantes jouables."""
    return {
        "code_length": CODE_LENGTH,
        "repetition_allowed": True,
        "modes": MODES,
        "variants": VARIANTS,
    }


@app.get("/api/games/current")
def current_game() -> PublicGame | None:
    """Retourne la partie active destinée au client, si elle existe."""
    game = get_current_game()
    return public_game(game) if game else None


@app.post("/api/games", status_code=201)
def new_game(payload: NewGameRequest) -> PublicGame:
    """Démarre une partie dans le mode ou la variante sélectionné."""
    known = payload.mode in MODES or payload.mode in VARIANTS
    if not known:
        raise HTTPException(status_code=400, detail="Mode de jeu inconnu")

    try:
        allowed_lengths = allowed_code_lengths(payload.mode)
        code_length = (
            payload.code_length
            if payload.code_length is not None
            else default_code_length(payload.mode)
        )
        if code_length not in allowed_lengths:
            raise ValueError("Longueur de code invalide pour cette variante")
        secret = generate_secret(payload.mode, code_length)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    now = utc_now()
    current = get_current_game()
    if current:
        abandon_active_games(
            now.isoformat(),
            {current["id"]: elapsed_seconds(current, now)},
        )

    game = create_game(
        payload.mode,
        secret,
        now.isoformat(),
        code_length=code_length,
    )
    return public_game(game)


@app.post("/api/games/{game_id}/guesses")
def submit_guess(game_id: str, payload: GuessRequest) -> PublicGame:
    """Valide une proposition, l'enregistre et termine une victoire."""
    game = get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Partie introuvable")
    if game["status"] != "active":
        raise HTTPException(status_code=409, detail="Cette partie est terminée")

    try:
        validate_guess(game["mode"], payload.guess, game["code_length"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    feedback = evaluate_variant_feedback(game["mode"], game["secret"], payload.guess)
    well_placed = feedback.count("well_placed")
    misplaced = feedback.count("misplaced")
    attempts: list[Attempt] = list(game["attempts"])
    now = utc_now()
    attempts.append(
        {
            "number": len(attempts) + 1,
            "guess": payload.guess,
            "well_placed": well_placed,
            "misplaced": misplaced,
            "result": compact_result(well_placed, misplaced),
            "feedback": feedback,
            "created_at": now.isoformat(),
        }
    )
    save_attempts(game_id, attempts)

    if well_placed == game["code_length"]:
        duration = elapsed_seconds(game, now)
        max_attempts = max_attempts_for(game["mode"])
        won_in_time = len(attempts) <= max_attempts
        score = (
            calculate_score(len(attempts), max_attempts, duration)
            if won_in_time
            else 0
        )
        finish_game(
            game_id,
            status="won" if won_in_time else "completed",
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
    """Abandonne une partie active et retourne son état public final."""
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
    """Retourne l'historique public des parties terminées."""
    return [public_game(game) for game in list_history(limit)]


@app.put("/api/games/{game_id}/player")
def save_player_name(game_id: str, payload: PlayerNameRequest) -> PublicGame:
    """Enregistre le pseudonyme d'une partie terminée."""
    game = get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Partie introuvable")
    player_name = " ".join(payload.player_name.split())
    if not 1 <= len(player_name) <= 20:
        raise HTTPException(
            status_code=400,
            detail="Le pseudonyme doit contenir entre 1 et 20 caractères",
        )
    if not re.fullmatch(r"[\w -]+", player_name, flags=re.UNICODE):
        raise HTTPException(
            status_code=400,
            detail="Le pseudonyme accepte uniquement lettres, chiffres, espaces, _ et -",
        )
    try:
        set_player_name(game_id, player_name)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    updated = get_game(game_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Partie introuvable")
    return public_game(updated)


@app.get("/api/stats")
def stats() -> Stats:
    """Retourne les statistiques agrégées des parties terminées."""
    return get_stats()


@app.delete("/api/scores")
def clear_scores() -> dict[str, int]:
    """Réinitialise l'historique et les scores des parties terminées."""
    return {"deleted_games": reset_scores()}
