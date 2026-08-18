from pathlib import Path


STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


def test_drag_and_drop_uses_pointer_events() -> None:
    """Le placement par glissement prend en charge la souris et le tactile."""
    script = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

    assert 'addEventListener("pointerdown"' in script
    assert 'addEventListener("pointermove", movePointerDrag' in script
    assert 'addEventListener("pointerup", finishPointerDrag' in script
    assert "elementFromPoint(clientX, clientY)" in script


def test_draggable_controls_disable_native_touch_gestures() -> None:
    """Les pions réservent les gestes tactiles au glisser-déposer du jeu."""
    stylesheet = (STATIC_DIR / "style.css").read_text(encoding="utf-8")

    assert stylesheet.count("touch-action: none") >= 2


def test_help_is_opened_in_a_dialog() -> None:
    """L'aide reste masquée jusqu'à l'activation du bouton dédié."""
    page = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    script = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

    assert 'id="open-help"' in page
    assert 'id="help-overlay" class="help-overlay" aria-hidden="true"' in page
    assert 'role="dialog" aria-modal="true"' in page
    assert 'els.openHelp.addEventListener("click", () =>' in script
    assert "showHelp();" in script


def test_finished_game_asks_for_player_name() -> None:
    """La fin de partie propose un pseudonyme pour l'historique des scores."""
    page = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    script = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

    assert 'id="player-name"' in page
    assert "async function savePlayerName()" in script
    assert 'method: "PUT"' in script
    assert '<th>Joueur</th>' in page


def test_finished_color_code_is_rendered_as_tokens() -> None:
    """Le message final affiche des pions plutôt que des codes hexadécimaux."""
    script = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

    assert "function renderFinishedMessage(prefix, suffix" in script
    assert "secret.appendChild(renderToken(value, state.game.mode, true))" in script
    assert 'state.game.secret.join(" · ")' not in script


def test_select_controls_match_the_application_style() -> None:
    """Les sélecteurs utilisent le style et la flèche propres à l'application."""
    stylesheet = (STATIC_DIR / "style.css").read_text(encoding="utf-8")

    assert "appearance: none" in stylesheet
    assert "background-image: url(\"data:image/svg+xml" in stylesheet
    assert "select:focus-visible" in stylesheet


def test_help_rule_titles_are_not_numbered() -> None:
    """Les titres des règles restent lisibles sans numérotation artificielle."""
    page = (STATIC_DIR / "index.html").read_text(encoding="utf-8")

    for number in range(1, 5):
        assert f"<strong>{number}." not in page


def test_hamburger_menu_contains_settings_and_score_reset() -> None:
    """Le menu hamburger expose les paramètres et la remise à zéro confirmée."""
    page = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    script = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

    assert 'id="open-settings" class="menu-button"' in page
    assert 'id="settings-overlay"' in page
    assert 'id="reset-scores"' in page
    assert "async function resetScoreHistory()" in script
    assert 'api("/api/scores", { method: "DELETE" })' in script
    assert "Clique une seconde fois pour confirmer." in script
