const state = {
    config: null,
    game: null,
    guess: [],
    receivedAt: Date.now(),
    suppressSlotClickUntil: 0,
    pointerDrag: null,
};

const els = {
    mode: document.querySelector("#mode"),
    difficulty: document.querySelector("#difficulty"),
    newGame: document.querySelector("#new-game"),
    giveUp: document.querySelector("#give-up"),
    timer: document.querySelector("#timer"),
    currentScore: document.querySelector("#current-score"),
    totalScore: document.querySelector("#total-score"),
    wins: document.querySelector("#wins"),
    modeTitle: document.querySelector("#mode-title"),
    currentGuess: document.querySelector("#current-guess"),
    palette: document.querySelector("#choice-palette"),
    backspace: document.querySelector("#backspace"),
    clear: document.querySelector("#clear"),
    submit: document.querySelector("#submit-guess"),
    message: document.querySelector("#message"),
    attempts: document.querySelector("#attempts"),
    history: document.querySelector("#history"),
    scoreHelp: document.querySelector("#score-help"),
    easyLegend: document.querySelector("#easy-legend"),
    victoryOverlay: document.querySelector("#victory-overlay"),
    victorySummary: document.querySelector("#victory-summary"),
    closeVictory: document.querySelector("#close-victory"),
    confetti: document.querySelector("#confetti"),
    endLabel: document.querySelector("#end-label"),
    endTitle: document.querySelector("#end-title"),
    playerName: document.querySelector("#player-name"),
    playerError: document.querySelector("#player-error"),
    savePlayer: document.querySelector("#save-player"),
    openHelp: document.querySelector("#open-help"),
    helpOverlay: document.querySelector("#help-overlay"),
    closeHelp: document.querySelector("#close-help"),
};

async function api(path, options = {}) {
    const response = await fetch(path, {
        headers: { "Content-Type": "application/json", ...(options.headers || {}) },
        ...options,
    });
    if (!response.ok) {
        let detail = "Erreur serveur";
        try {
            const body = await response.json();
            detail = body.detail || detail;
        } catch (_) {
            // Keep the generic message.
        }
        throw new Error(detail);
    }
    return response.status === 204 ? null : response.json();
}

function formatTime(totalSeconds) {
    const seconds = Math.max(0, Math.floor(totalSeconds || 0));
    const minutes = Math.floor(seconds / 60);
    const rest = seconds % 60;
    return `${String(minutes).padStart(2, "0")}:${String(rest).padStart(2, "0")}`;
}

function modeConfig(mode = state.game?.mode || els.mode.value) {
    return state.config?.modes?.[mode];
}

function choiceByValue(value, mode = state.game?.mode || els.mode.value) {
    return modeConfig(mode)?.choices.find((choice) => choice.value === value);
}

function blankGuess() {
    return Array(state.config?.code_length || 4).fill(null);
}

function isGuessComplete() {
    return state.guess.length === state.config.code_length && state.guess.every(Boolean);
}

function isEasyMode() {
    return els.difficulty?.value === "easy";
}

function feedbackLabel(status) {
    if (status === "well_placed") return { icon: "✓", text: "Bien placé" };
    if (status === "misplaced") return { icon: "↔", text: "Mal placé" };
    if (status === "absent") return { icon: "✕", text: "Absent" };
    return { icon: "?", text: "Indice indisponible" };
}

function renderToken(value, mode, small = false) {
    const choice = choiceByValue(value, mode);
    const token = document.createElement("span");
    token.className = `token${small ? " small" : ""}`;
    token.title = choice?.label || value;
    if (mode === "colors" && choice) {
        token.style.background = choice.value;
        token.setAttribute("aria-label", choice.label);
    } else {
        token.textContent = choice?.label || value;
    }
    return token;
}

function renderModeSelector() {
    els.mode.innerHTML = "";
    Object.entries(state.config.modes).forEach(([key, config]) => {
        const option = document.createElement("option");
        option.value = key;
        option.textContent = config.label;
        els.mode.appendChild(option);
    });
}

function addChoice(value) {
    if (!state.game || state.game.status !== "active") return;
    const emptyIndex = state.guess.findIndex((entry) => !entry);
    if (emptyIndex === -1) return;
    state.guess[emptyIndex] = value;
    renderCurrentGuess();
}

function clearDropTargets() {
    document.querySelectorAll(".guess-slot.drop-target").forEach((slot) => {
        slot.classList.remove("drop-target");
    });
}

function slotAtPoint(clientX, clientY) {
    return document.elementFromPoint(clientX, clientY)?.closest(".guess-slot") || null;
}

function startPointerDrag(event, source, payload) {
    if (event.button !== 0 || !state.game || state.game.status !== "active") return;
    state.pointerDrag = {
        pointerId: event.pointerId,
        source,
        payload,
        startX: event.clientX,
        startY: event.clientY,
        moved: false,
    };
    source.setPointerCapture(event.pointerId);
}

function movePointerDrag(event) {
    const drag = state.pointerDrag;
    if (!drag || drag.pointerId !== event.pointerId) return;
    const distance = Math.hypot(event.clientX - drag.startX, event.clientY - drag.startY);
    if (!drag.moved && distance < 6) return;
    drag.moved = true;
    event.preventDefault();
    drag.source.classList.add("dragging");
    clearDropTargets();
    slotAtPoint(event.clientX, event.clientY)?.classList.add("drop-target");
}

function finishPointerDrag(event) {
    const drag = state.pointerDrag;
    if (!drag || drag.pointerId !== event.pointerId) return;
    state.pointerDrag = null;
    drag.source.classList.remove("dragging");
    const target = drag.moved ? slotAtPoint(event.clientX, event.clientY) : null;
    clearDropTargets();
    if (!target) return;

    const targetIndex = Number(target.dataset.index);
    if (!Number.isInteger(targetIndex)) return;
    if (drag.payload.type === "palette") {
        state.guess[targetIndex] = drag.payload.value;
    } else if (drag.payload.type === "slot") {
        const sourceIndex = drag.payload.index;
        const targetValue = state.guess[targetIndex];
        state.guess[targetIndex] = state.guess[sourceIndex];
        state.guess[sourceIndex] = targetValue;
    }
    state.suppressSlotClickUntil = Date.now() + 350;
    renderCurrentGuess();
}

function cancelPointerDrag(event) {
    const drag = state.pointerDrag;
    if (!drag || drag.pointerId !== event.pointerId) return;
    drag.source.classList.remove("dragging");
    state.pointerDrag = null;
    clearDropTargets();
}

function renderPalette() {
    els.palette.innerHTML = "";
    const config = modeConfig();
    if (!config) return;
    els.modeTitle.textContent = `Mode ${config.label} — choisis 4 valeurs`;

    config.choices.forEach((choice) => {
        const button = document.createElement("button");
        button.className = "choice-button";
        button.type = "button";
        button.title = `${choice.label} — cliquer ou glisser`;
        button.setAttribute("aria-label", choice.label);
        if ((state.game?.mode || els.mode.value) === "colors") {
            button.style.background = choice.value;
        } else {
            button.textContent = choice.label;
        }
        button.addEventListener("click", () => {
            if (Date.now() < state.suppressSlotClickUntil) return;
            addChoice(choice.value);
        });
        button.addEventListener("pointerdown", (event) => {
            startPointerDrag(event, button, { type: "palette", value: choice.value });
        });
        els.palette.appendChild(button);
    });
}

function renderCurrentGuess() {
    els.currentGuess.innerHTML = "";
    for (let index = 0; index < state.config.code_length; index += 1) {
        const value = state.guess[index];
        const slot = document.createElement("div");
        slot.className = `guess-slot${value ? " filled" : ""}`;
        slot.dataset.index = String(index);
        slot.title = value ? "Cliquer pour enlever, ou glisser pour déplacer" : "Dépose un pion ici";

        if (value) {
            slot.appendChild(renderToken(value, state.game?.mode || els.mode.value));
            slot.setAttribute("role", "button");
            slot.setAttribute("tabindex", "0");
            slot.setAttribute("aria-label", `Position ${index + 1}, cliquer pour retirer`);
            slot.addEventListener("click", () => {
                if (Date.now() < state.suppressSlotClickUntil) return;
                state.guess[index] = null;
                renderCurrentGuess();
            });
            slot.addEventListener("keydown", (event) => {
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    state.guess[index] = null;
                    renderCurrentGuess();
                }
            });
            slot.addEventListener("pointerdown", (event) => {
                startPointerDrag(event, slot, { type: "slot", index, value });
            });
        } else {
            const empty = document.createElement("span");
            empty.className = "token empty";
            empty.textContent = "?";
            slot.appendChild(empty);
        }

        els.currentGuess.appendChild(slot);
    }
    els.submit.disabled = !state.game || state.game.status !== "active" || !isGuessComplete();
}

document.addEventListener("pointermove", movePointerDrag, { passive: false });
document.addEventListener("pointerup", finishPointerDrag);
document.addEventListener("pointercancel", cancelPointerDrag);

function renderAttemptToken(attempt, value, index) {
    if (!isEasyMode()) return renderToken(value, state.game.mode, true);

    const status = attempt.feedback?.[index];
    const label = feedbackLabel(status);
    const wrapper = document.createElement("span");
    wrapper.className = `easy-feedback feedback-${status || "unknown"}`;
    wrapper.title = `${choiceByValue(value, state.game.mode)?.label || value} : ${label.text}`;

    wrapper.appendChild(renderToken(value, state.game.mode, true));

    const hint = document.createElement("small");
    hint.className = "easy-feedback-label";
    hint.textContent = `${label.icon} ${label.text}`;
    wrapper.appendChild(hint);
    return wrapper;
}

function renderAttempts() {
    els.attempts.innerHTML = "";
    if (els.easyLegend) els.easyLegend.hidden = !isEasyMode();

    const attempts = state.game?.attempts || [];
    if (!attempts.length) {
        els.attempts.innerHTML = '<p class="empty-state">Aucune tentative pour le moment.</p>';
        els.scoreHelp.textContent = isEasyMode()
            ? "En mode facile, chaque pion recevra un indice après validation."
            : "Aucune tentative pour le moment.";
        return;
    }

    const latest = attempts[attempts.length - 1];
    els.scoreHelp.textContent = `Ton résultat : ${latest.result} — ${latest.well_placed} bien placée(s), ${latest.misplaced} mal placée(s).`;

    [...attempts].reverse().forEach((attempt) => {
        const row = document.createElement("div");
        row.className = `attempt-row${isEasyMode() ? " easy-attempt" : ""}`;

        const number = document.createElement("strong");
        number.textContent = `#${attempt.number}`;
        row.appendChild(number);

        const tokens = document.createElement("div");
        tokens.className = "attempt-tokens";
        attempt.guess.forEach((value, index) => tokens.appendChild(renderAttemptToken(attempt, value, index)));
        row.appendChild(tokens);

        const result = document.createElement("span");
        result.className = "result-badge";
        result.textContent = attempt.result;
        result.title = `${attempt.well_placed} bien placée(s), ${attempt.misplaced} mal placée(s)`;
        row.appendChild(result);

        els.attempts.appendChild(row);
    });
}

function renderGame() {
    state.receivedAt = Date.now();
    state.guess = blankGuess();
    if (!state.game) {
        els.message.textContent = "Aucune partie en cours. Choisis un mode et lance une partie.";
        els.timer.textContent = "00:00";
        els.currentScore.textContent = "0";
        els.giveUp.disabled = true;
        renderPalette();
        renderCurrentGuess();
        renderAttempts();
        return;
    }

    els.mode.value = state.game.mode;
    els.giveUp.disabled = state.game.status !== "active";
    renderPalette();
    renderCurrentGuess();
    renderAttempts();

    if (state.game.status === "won") {
        els.message.textContent = `Gagné ! Code : ${state.game.secret.join(" · ")} — score ${state.game.score}`;
    } else if (state.game.status === "completed") {
        els.message.textContent = `Code trouvé hors limite. Il fallait réussir en moins de 10 essais.`;
    } else if (state.game.status === "lost") {
        els.message.textContent = `Partie abandonnée. Code : ${state.game.secret.join(" · ")}`;
    } else if (state.game.status === "abandoned") {
        els.message.textContent = "Partie remplacée par une nouvelle partie.";
    } else if (isEasyMode()) {
        els.message.textContent = "Mode facile enfant : après chaque essai, regarde l'indice sous chaque pion.";
    } else {
        els.message.textContent = "Trouve la combinaison secrète.";
    }
    updateClock();
}

function updateClock() {
    if (!state.game) return;
    let elapsed = state.game.elapsed_seconds || 0;
    if (state.game.status === "active") {
        elapsed += Math.floor((Date.now() - state.receivedAt) / 1000);
    }
    els.timer.textContent = formatTime(elapsed);
    if (state.game.status === "active") {
        const score = Math.max(0, 900 - state.game.attempts.length * 100);
        els.currentScore.textContent = String(score);
    } else {
        els.currentScore.textContent = String(state.game.score || 0);
    }
}

function showEndDialog() {
    if (!state.game || state.game.status === "active") return;
    const won = state.game.status === "won";
    els.endLabel.textContent = won ? "Victoire" : "Partie terminée";
    els.endTitle.textContent = won
        ? "Combinaison trouvée !"
        : state.game.status === "completed"
            ? "Code trouvé hors limite"
            : "Partie abandonnée";
    els.victorySummary.textContent = `${state.game.attempts.length} essai(s) · score ${state.game.score}`;
    els.playerName.value = state.game.player_name || localStorage.getItem("mastermind-player-name") || "";
    els.playerError.textContent = "";
    els.confetti.innerHTML = "";
    if (won) {
        const colors = ["#ef4444", "#3b82f6", "#22c55e", "#eab308", "#a855f7", "#f97316"];
        for (let index = 0; index < 70; index += 1) {
            const piece = document.createElement("span");
            piece.className = "confetti-piece";
            piece.style.left = `${Math.random() * 100}%`;
            piece.style.background = colors[index % colors.length];
            piece.style.animationDelay = `${Math.random() * 0.65}s`;
            piece.style.animationDuration = `${1.8 + Math.random() * 1.5}s`;
            piece.style.setProperty("--spin", `${360 + Math.floor(Math.random() * 720)}deg`);
            els.confetti.appendChild(piece);
        }
    }
    els.victoryOverlay.classList.add("visible");
    els.victoryOverlay.setAttribute("aria-hidden", "false");
    els.playerName.focus();
}

function hideVictory() {
    els.victoryOverlay.classList.remove("visible");
    els.victoryOverlay.setAttribute("aria-hidden", "true");
    els.confetti.innerHTML = "";
}

async function savePlayerName() {
    if (!state.game || state.game.status === "active") return;
    const playerName = els.playerName.value.trim();
    if (!playerName) {
        els.playerError.textContent = "Entre un pseudonyme.";
        els.playerName.focus();
        return;
    }
    try {
        state.game = await api(`/api/games/${state.game.id}/player`, {
            method: "PUT",
            body: JSON.stringify({ player_name: playerName }),
        });
        localStorage.setItem("mastermind-player-name", state.game.player_name);
        await loadHistory();
        hideVictory();
    } catch (error) {
        els.playerError.textContent = error.message;
    }
}

function showHelp() {
    els.helpOverlay.classList.add("visible");
    els.helpOverlay.setAttribute("aria-hidden", "false");
    els.closeHelp.focus();
}

function hideHelp() {
    els.helpOverlay.classList.remove("visible");
    els.helpOverlay.setAttribute("aria-hidden", "true");
    els.openHelp.focus();
}

async function loadStats() {
    const stats = await api("/api/stats");
    els.totalScore.textContent = String(stats.total_score);
    els.wins.textContent = `${stats.wins}/${stats.games_total}`;
}

async function loadHistory() {
    const history = await api("/api/history?limit=50");
    els.history.innerHTML = "";
    if (!history.length) {
        const row = document.createElement("tr");
        row.innerHTML = '<td colspan="7" class="empty-state">Aucune partie terminée.</td>';
        els.history.appendChild(row);
        return;
    }

    history.forEach((game) => {
        const row = document.createElement("tr");
        const label = state.config.modes[game.mode]?.label || game.mode;
        const status = game.status === "won"
            ? "Gagnée"
            : game.status === "completed"
                ? "Terminée hors limite"
                : game.status === "lost"
                    ? "Abandonnée"
                    : "Remplacée";
        const secret = game.secret.map((value) => choiceByValue(value, game.mode)?.label || value).join(" · ");
        row.innerHTML = `
            <td>${label}</td>
            <td>${game.player_name || "—"}</td>
            <td>${status}</td>
            <td>${game.attempts.length}</td>
            <td>${formatTime(game.elapsed_seconds)}</td>
            <td>${game.score}</td>
            <td>${secret}</td>
        `;
        els.history.appendChild(row);
    });
}

async function startGame() {
    try {
        hideVictory();
        state.game = await api("/api/games", {
            method: "POST",
            body: JSON.stringify({ mode: els.mode.value }),
        });
        renderGame();
        await Promise.all([loadStats(), loadHistory()]);
    } catch (error) {
        els.message.textContent = error.message;
    }
}

async function submitGuess() {
    if (!state.game || !isGuessComplete()) return;
    try {
        state.game = await api(`/api/games/${state.game.id}/guesses`, {
            method: "POST",
            body: JSON.stringify({ guess: state.guess }),
        });
        renderGame();
        if (state.game.status !== "active") {
            await Promise.all([loadStats(), loadHistory()]);
        }
        if (state.game.status !== "active") showEndDialog();
    } catch (error) {
        els.message.textContent = error.message;
    }
}

async function giveUp() {
    if (!state.game || state.game.status !== "active") return;
    try {
        state.game = await api(`/api/games/${state.game.id}/give-up`, { method: "POST" });
        renderGame();
        await Promise.all([loadStats(), loadHistory()]);
        showEndDialog();
    } catch (error) {
        els.message.textContent = error.message;
    }
}

async function init() {
    try {
        state.config = await api("/api/modes");
        state.guess = blankGuess();
        renderModeSelector();
        const savedDifficulty = localStorage.getItem("mastermind-difficulty");
        if (savedDifficulty === "easy" || savedDifficulty === "normal") {
            els.difficulty.value = savedDifficulty;
        }
        state.game = await api("/api/games/current");
        if (state.game) els.mode.value = state.game.mode;
        renderGame();
        await Promise.all([loadStats(), loadHistory()]);
    } catch (error) {
        els.message.textContent = `Impossible de charger le jeu : ${error.message}`;
    }
}

els.newGame.addEventListener("click", startGame);
els.submit.addEventListener("click", submitGuess);
els.giveUp.addEventListener("click", giveUp);
els.backspace.addEventListener("click", () => {
    for (let index = state.guess.length - 1; index >= 0; index -= 1) {
        if (state.guess[index]) {
            state.guess[index] = null;
            break;
        }
    }
    renderCurrentGuess();
});
els.clear.addEventListener("click", () => {
    state.guess = blankGuess();
    renderCurrentGuess();
});
els.mode.addEventListener("change", renderPalette);
els.difficulty.addEventListener("change", () => {
    localStorage.setItem("mastermind-difficulty", els.difficulty.value);
    renderAttempts();
    if (state.game?.status === "active") {
        els.message.textContent = isEasyMode()
            ? "Mode facile enfant : après chaque essai, regarde l'indice sous chaque pion."
            : "Trouve la combinaison secrète.";
    }
});
els.closeVictory.addEventListener("click", hideVictory);
els.savePlayer.addEventListener("click", savePlayerName);
els.playerName.addEventListener("keydown", (event) => {
    if (event.key === "Enter") savePlayerName();
});
els.openHelp.addEventListener("click", showHelp);
els.closeHelp.addEventListener("click", hideHelp);
els.helpOverlay.addEventListener("click", (event) => {
    if (event.target === els.helpOverlay) hideHelp();
});
els.victoryOverlay.addEventListener("click", (event) => {
    if (event.target === els.victoryOverlay) hideVictory();
});
document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && els.victoryOverlay.classList.contains("visible")) hideVictory();
    if (event.key === "Escape" && els.helpOverlay.classList.contains("visible")) hideHelp();
});

setInterval(updateClock, 1000);
init();
