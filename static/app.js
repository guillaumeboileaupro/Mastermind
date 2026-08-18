const state = {
    config: null,
    game: null,
    guess: [],
    receivedAt: Date.now(),
};

const els = {
    mode: document.querySelector("#mode"),
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

function renderToken(value, mode, small = false) {
    const choice = choiceByValue(value, mode);
    const token = document.createElement("span");
    token.className = `token${small ? " small" : ""}`;
    token.title = choice?.label || value;
    if (mode === "colors" && choice?.color) {
        token.style.background = choice.color;
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

function renderPalette() {
    els.palette.innerHTML = "";
    const config = modeConfig();
    if (!config) return;
    els.modeTitle.textContent = `Mode ${config.label} — choisis 4 valeurs`;

    config.choices.forEach((choice) => {
        const button = document.createElement("button");
        button.className = "choice-button";
        button.type = "button";
        button.title = choice.label;
        button.setAttribute("aria-label", choice.label);
        if (state.game?.mode === "colors") {
            button.style.background = choice.color;
        } else {
            button.textContent = choice.label;
        }
        button.addEventListener("click", () => {
            if (!state.game || state.game.status !== "active") return;
            if (state.guess.length >= state.config.code_length) return;
            state.guess.push(choice.value);
            renderCurrentGuess();
        });
        els.palette.appendChild(button);
    });
}

function renderCurrentGuess() {
    els.currentGuess.innerHTML = "";
    for (let index = 0; index < state.config.code_length; index += 1) {
        if (state.guess[index]) {
            els.currentGuess.appendChild(renderToken(state.guess[index], state.game?.mode));
        } else {
            const empty = document.createElement("span");
            empty.className = "token empty";
            empty.textContent = "?";
            els.currentGuess.appendChild(empty);
        }
    }
    els.submit.disabled = !state.game || state.game.status !== "active" || state.guess.length !== state.config.code_length;
}

function renderAttempts() {
    els.attempts.innerHTML = "";
    const attempts = state.game?.attempts || [];
    if (!attempts.length) {
        els.attempts.innerHTML = '<p class="empty-state">Aucune tentative pour le moment.</p>';
        return;
    }

    [...attempts].reverse().forEach((attempt) => {
        const row = document.createElement("div");
        row.className = "attempt-row";

        const number = document.createElement("strong");
        number.textContent = `#${attempt.number}`;
        row.appendChild(number);

        const tokens = document.createElement("div");
        tokens.className = "attempt-tokens";
        attempt.guess.forEach((value) => tokens.appendChild(renderToken(value, state.game.mode, true)));
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
    state.guess = [];
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
    } else if (state.game.status === "lost") {
        els.message.textContent = `Partie abandonnée. Code : ${state.game.secret.join(" · ")}`;
    } else if (state.game.status === "abandoned") {
        els.message.textContent = "Partie remplacée par une nouvelle partie.";
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
        const score = Math.max(0, 1000 - state.game.attempts.length * 100 - elapsed);
        els.currentScore.textContent = String(score);
    } else {
        els.currentScore.textContent = String(state.game.score || 0);
    }
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
        row.innerHTML = '<td colspan="6" class="empty-state">Aucune partie terminée.</td>';
        els.history.appendChild(row);
        return;
    }

    history.forEach((game) => {
        const row = document.createElement("tr");
        const label = state.config.modes[game.mode]?.label || game.mode;
        const status = game.status === "won" ? "Gagnée" : game.status === "lost" ? "Abandonnée" : "Remplacée";
        const secret = game.secret.map((value) => choiceByValue(value, game.mode)?.label || value).join(" · ");
        row.innerHTML = `
            <td>${label}</td>
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
    if (!state.game || state.guess.length !== state.config.code_length) return;
    try {
        state.game = await api(`/api/games/${state.game.id}/guesses`, {
            method: "POST",
            body: JSON.stringify({ guess: state.guess }),
        });
        renderGame();
        if (state.game.status !== "active") {
            await Promise.all([loadStats(), loadHistory()]);
        }
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
    } catch (error) {
        els.message.textContent = error.message;
    }
}

async function init() {
    try {
        state.config = await api("/api/modes");
        renderModeSelector();
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
    state.guess.pop();
    renderCurrentGuess();
});
els.clear.addEventListener("click", () => {
    state.guess = [];
    renderCurrentGuess();
});
els.mode.addEventListener("change", renderPalette);

setInterval(updateClock, 1000);
init();
