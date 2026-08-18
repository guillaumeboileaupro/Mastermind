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
    codeLength: document.querySelector("#code-length"),
    codeLengthGroup: document.querySelector("#code-length-group"),
    variantMeta: document.querySelector("#variant-meta"),
    rulesSummary: document.querySelector("#rules-summary"),
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
    openSettings: document.querySelector("#open-settings"),
    settingsOverlay: document.querySelector("#settings-overlay"),
    closeSettings: document.querySelector("#close-settings"),
    resetScores: document.querySelector("#reset-scores"),
    resetConfirmation: document.querySelector("#reset-confirmation"),
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

function canonicalMode(mode) {
    if (state.config?.variants?.[mode]) return mode;
    if (mode === "colors") return "mastermind-1972";
    if (mode === "digits") return "number-mastermind-1976";
    return mode;
}

function modeConfig(mode = state.game?.mode || els.mode.value) {
    return state.config?.variants?.[mode]
        || state.config?.modes?.[mode]
        || state.config?.variants?.[canonicalMode(mode)];
}

function currentMode() {
    return state.game?.status === "active" ? state.game.mode : els.mode.value;
}

function currentCodeLength() {
    if (state.game) return state.game.code_length || state.config?.code_length || 4;
    const config = modeConfig(els.mode.value);
    return Number(els.codeLength?.value)
        || config?.default_code_length
        || state.config?.code_length
        || 4;
}

function currentMaxAttempts() {
    if (state.game) return state.game.max_attempts || 10;
    return modeConfig(els.mode.value)?.max_attempts || 10;
}

function choiceByValue(value, mode = currentMode()) {
    return modeConfig(mode)?.choices.find((choice) => choice.value === value);
}

function blankGuess() {
    return Array(currentCodeLength()).fill(null);
}

function isGuessComplete() {
    return state.guess.length === currentCodeLength() && state.guess.every(Boolean);
}

function isEasyMode() {
    return els.difficulty?.value === "easy";
}

function usesAlphabetFeedback(mode = state.game?.mode || els.mode.value) {
    return modeConfig(mode)?.feedback_kind === "alphabet";
}

function feedbackLabel(status) {
    if (status === "well_placed") return { icon: "✓", text: "Bien placé" };
    if (status === "misplaced") return { icon: "↔", text: "Mal placé" };
    if (status === "absent") return { icon: "✕", text: "Absent" };
    if (status === "higher") return { icon: "↑", text: "Plus tard" };
    if (status === "lower") return { icon: "↓", text: "Plus tôt" };
    return { icon: "?", text: "Indice indisponible" };
}

function applyChoiceAppearance(element, choice) {
    if (!choice) return;
    const color = choice.color || (String(choice.value).startsWith("#") ? choice.value : null);
    if (color) {
        element.style.background = color;
        element.dataset.hasColor = "true";
    }
    if (choice.symbol) {
        const symbol = document.createElement("span");
        symbol.className = "choice-symbol";
        symbol.textContent = choice.symbol;
        element.appendChild(symbol);
    } else if (!color) {
        element.textContent = choice.label;
    }
}

function renderToken(value, mode, small = false) {
    const choice = choiceByValue(value, mode);
    const token = document.createElement("span");
    token.className = `token${small ? " small" : ""}`;
    token.title = choice?.label || value;
    token.setAttribute("aria-label", choice?.label || value);
    if (choice) applyChoiceAppearance(token, choice);
    else token.textContent = value;
    return token;
}

function renderModeSelector() {
    els.mode.innerHTML = "";
    Object.entries(state.config.variants || {}).forEach(([key, config]) => {
        const option = document.createElement("option");
        option.value = key;
        option.textContent = `${config.label} · ${config.year}`;
        els.mode.appendChild(option);
    });
}

function renderVariantControls() {
    const config = modeConfig(els.mode.value);
    if (!config) return;
    const lengths = config.code_lengths || [state.config.code_length || 4];
    const previous = Number(els.codeLength.value);
    els.codeLength.innerHTML = "";
    lengths.forEach((length) => {
        const option = document.createElement("option");
        option.value = String(length);
        option.textContent = `${length} positions`;
        els.codeLength.appendChild(option);
    });
    const preferred = lengths.includes(previous) ? previous : config.default_code_length || lengths[0];
    els.codeLength.value = String(preferred);
    els.codeLengthGroup.hidden = lengths.length <= 1;
    const attempts = config.max_attempts || 10;
    els.variantMeta.textContent = `${config.description || ""} ${config.note || ""}`.trim();
    els.rulesSummary.textContent = `${preferred} positions · ${config.choices.length} choix · ${attempts} essais avec score.`;
    if (!state.game || state.game.status !== "active") {
        state.game = null;
        state.guess = blankGuess();
        renderPalette();
        renderCurrentGuess();
        renderAttempts();
    }
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
    const mode = currentMode();
    const config = modeConfig(mode);
    if (!config) return;
    const length = currentCodeLength();
    els.modeTitle.textContent = `${config.label} — choisis ${length} valeurs`;

    config.choices.forEach((choice) => {
        const button = document.createElement("button");
        button.className = "choice-button";
        button.type = "button";
        button.title = `${choice.label} — cliquer ou glisser`;
        button.setAttribute("aria-label", choice.label);
        applyChoiceAppearance(button, choice);
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
    const length = currentCodeLength();
    if (state.guess.length !== length) state.guess = Array(length).fill(null);
    for (let index = 0; index < length; index += 1) {
        const value = state.guess[index];
        const slot = document.createElement("div");
        slot.className = `guess-slot${value ? " filled" : ""}`;
        slot.dataset.index = String(index);
        slot.title = value ? "Cliquer pour enlever, ou glisser pour déplacer" : "Dépose un pion ici";

        if (value) {
            slot.appendChild(renderToken(value, currentMode()));
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
    const showHint = isEasyMode() || usesAlphabetFeedback(state.game?.mode);
    if (!showHint) return renderToken(value, state.game.mode, true);

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
    const alphabet = usesAlphabetFeedback(state.game?.mode);
    if (els.easyLegend) els.easyLegend.hidden = !isEasyMode() || alphabet;

    const attempts = state.game?.attempts || [];
    if (!attempts.length) {
        els.attempts.innerHTML = '<p class="empty-state">Aucune tentative pour le moment.</p>';
        els.scoreHelp.textContent = alphabet
            ? "Les flèches indiqueront si chaque lettre secrète est plus tôt ou plus tard dans l’alphabet."
            : isEasyMode()
                ? "En mode facile, chaque pion recevra un indice après validation."
                : "Aucune tentative pour le moment.";
        return;
    }

    const latest = attempts[attempts.length - 1];
    els.scoreHelp.textContent = alphabet
        ? `${latest.well_placed} lettre(s) exactement placée(s) — suis les flèches sous les autres lettres.`
        : `Ton résultat : ${latest.result} — ${latest.well_placed} bien placée(s), ${latest.misplaced} mal placée(s).`;

    [...attempts].reverse().forEach((attempt) => {
        const row = document.createElement("div");
        row.className = `attempt-row${(isEasyMode() || alphabet) ? " easy-attempt" : ""}`;

        const number = document.createElement("strong");
        number.textContent = `#${attempt.number}`;
        row.appendChild(number);

        const tokens = document.createElement("div");
        tokens.className = "attempt-tokens";
        attempt.guess.forEach((value, index) => {
            tokens.appendChild(renderAttemptToken(attempt, value, index));
        });
        row.appendChild(tokens);

        const result = document.createElement("span");
        result.className = "result-badge";
        result.textContent = alphabet ? `${latest.well_placed}/${state.game.code_length}` : attempt.result;
        result.title = alphabet
            ? `${attempt.well_placed} position(s) exacte(s)`
            : `${attempt.well_placed} bien placée(s), ${attempt.misplaced} mal placée(s)`;
        row.appendChild(result);
        els.attempts.appendChild(row);
    });
}

function renderFinishedMessage(prefix, suffix = "") {
    els.message.textContent = `${prefix} `;
    const secret = document.createElement("span");
    secret.className = "message-secret";
    state.game.secret.forEach((value) => {
        secret.appendChild(renderToken(value, state.game.mode, true));
    });
    els.message.appendChild(secret);
    if (suffix) els.message.append(` ${suffix}`);
}

function renderGame() {
    state.receivedAt = Date.now();
    state.guess = blankGuess();
    if (!state.game) {
        els.message.textContent = "Choisis une variante puis lance une partie.";
        els.timer.textContent = "00:00";
        els.currentScore.textContent = "0";
        els.giveUp.disabled = true;
        renderPalette();
        renderCurrentGuess();
        renderAttempts();
        return;
    }

    const selectable = canonicalMode(state.game.mode);
    if (state.config.variants?.[selectable]) els.mode.value = selectable;
    const config = modeConfig(state.game.mode);
    els.rulesSummary.textContent = `${state.game.code_length} positions · ${config?.choices.length || "?"} choix · ${state.game.max_attempts} essais avec score.`;
    els.variantMeta.textContent = `${config?.description || ""} ${config?.note || ""}`.trim();
    els.giveUp.disabled = state.game.status !== "active";
    renderPalette();
    renderCurrentGuess();
    renderAttempts();

    if (state.game.status === "won") {
        renderFinishedMessage("Gagné ! Code :", `— score ${state.game.score}`);
    } else if (state.game.status === "completed") {
        els.message.textContent = `Code trouvé hors limite. Il fallait réussir en ${state.game.max_attempts} essais maximum.`;
    } else if (state.game.status === "lost") {
        renderFinishedMessage("Partie abandonnée. Code :");
    } else if (state.game.status === "abandoned") {
        els.message.textContent = "Partie remplacée par une nouvelle partie.";
    } else if (usesAlphabetFeedback(state.game.mode)) {
        els.message.textContent = "Utilise les flèches pour te rapprocher des lettres secrètes.";
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
        const score = Math.max(0, currentMaxAttempts() * 100 - state.game.attempts.length * 100);
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
        const colors = ["#ef4444", "#3b82f6", "#22c55e", "#eab308", "#8b5cf6", "#f97316"];
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

function showSettings() {
    els.settingsOverlay.classList.add("visible");
    els.settingsOverlay.setAttribute("aria-hidden", "false");
    els.openSettings.setAttribute("aria-expanded", "true");
    els.closeSettings.focus();
}

function hideSettings() {
    els.settingsOverlay.classList.remove("visible");
    els.settingsOverlay.setAttribute("aria-hidden", "true");
    els.openSettings.setAttribute("aria-expanded", "false");
    els.resetScores.dataset.confirming = "false";
    els.resetScores.textContent = "Réinitialiser les scores";
    els.resetConfirmation.textContent = "";
    els.openSettings.focus();
}

async function resetScoreHistory() {
    if (els.resetScores.dataset.confirming !== "true") {
        els.resetScores.dataset.confirming = "true";
        els.resetScores.textContent = "Confirmer la réinitialisation";
        els.resetConfirmation.textContent = "Clique une seconde fois pour confirmer.";
        return;
    }
    try {
        const result = await api("/api/scores", { method: "DELETE" });
        await Promise.all([loadStats(), loadHistory()]);
        els.resetScores.dataset.confirming = "false";
        els.resetScores.textContent = "Réinitialiser les scores";
        els.resetConfirmation.textContent = `${result.deleted_games} partie(s) supprimée(s).`;
    } catch (error) {
        els.resetConfirmation.textContent = error.message;
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
        row.innerHTML = '<td colspan="7" class="empty-state">Aucune partie terminée.</td>';
        els.history.appendChild(row);
        return;
    }

    history.forEach((game) => {
        const row = document.createElement("tr");
        const config = modeConfig(game.mode);
        const label = config?.label || game.mode;
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
            body: JSON.stringify({
                mode: els.mode.value,
                code_length: Number(els.codeLength.value) || undefined,
            }),
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
            showEndDialog();
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
        showEndDialog();
    } catch (error) {
        els.message.textContent = error.message;
    }
}

async function init() {
    try {
        state.config = await api("/api/modes");
        renderModeSelector();
        if (state.config.variants?.["mastermind-1972"]) els.mode.value = "mastermind-1972";
        renderVariantControls();
        const savedDifficulty = localStorage.getItem("mastermind-difficulty");
        if (savedDifficulty === "easy" || savedDifficulty === "normal") {
            els.difficulty.value = savedDifficulty;
        }
        state.game = await api("/api/games/current");
        if (state.game) {
            const selectable = canonicalMode(state.game.mode);
            if (state.config.variants?.[selectable]) els.mode.value = selectable;
        }
        state.guess = blankGuess();
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
els.mode.addEventListener("change", renderVariantControls);
els.codeLength.addEventListener("change", () => {
    if (!state.game || state.game.status !== "active") {
        state.game = null;
        state.guess = blankGuess();
        renderVariantControls();
    }
});
els.difficulty.addEventListener("change", () => {
    localStorage.setItem("mastermind-difficulty", els.difficulty.value);
    renderAttempts();
    if (state.game?.status === "active") {
        els.message.textContent = usesAlphabetFeedback(state.game.mode)
            ? "Utilise les flèches pour te rapprocher des lettres secrètes."
            : isEasyMode()
                ? "Mode facile enfant : après chaque essai, regarde l'indice sous chaque pion."
                : "Trouve la combinaison secrète.";
    }
});
els.closeVictory.addEventListener("click", hideVictory);
els.savePlayer.addEventListener("click", savePlayerName);
els.playerName.addEventListener("keydown", (event) => {
    if (event.key === "Enter") savePlayerName();
});
els.openHelp.addEventListener("click", () => {
    hideSettings();
    showHelp();
});
els.closeHelp.addEventListener("click", hideHelp);
els.helpOverlay.addEventListener("click", (event) => {
    if (event.target === els.helpOverlay) hideHelp();
});
els.openSettings.addEventListener("click", showSettings);
els.closeSettings.addEventListener("click", hideSettings);
els.resetScores.addEventListener("click", resetScoreHistory);
els.settingsOverlay.addEventListener("click", (event) => {
    if (event.target === els.settingsOverlay) hideSettings();
});
els.victoryOverlay.addEventListener("click", (event) => {
    if (event.target === els.victoryOverlay) hideVictory();
});
document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && els.victoryOverlay.classList.contains("visible")) hideVictory();
    if (event.key === "Escape" && els.helpOverlay.classList.contains("visible")) hideHelp();
    if (event.key === "Escape" && els.settingsOverlay.classList.contains("visible")) hideSettings();
});

setInterval(updateClock, 1000);
init();
