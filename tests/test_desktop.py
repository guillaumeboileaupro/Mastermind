import os
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PyQt6.QtWidgets import QApplication, QMessageBox

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import desktop
from app import storage
from app.game import MODES
from app.types import Attempt


@pytest.fixture(scope="module")
def qt_app() -> Iterator[QApplication]:
    """Fournit une application Qt hors écran aux tests de fenêtre native."""
    app = desktop.configure_qt_identity()
    yield app


@pytest.fixture
def window(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, qt_app: QApplication,
) -> Iterator[desktop.MastermindWindow]:
    """Construit une fenêtre connectée à une base temporaire."""
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "desktop-test.db")
    storage.init_db()
    widget = desktop.MastermindWindow()
    yield widget
    widget.close()


def test_resource_path_is_relative_to_desktop_module() -> None:
    """Les ressources sont résolues depuis le dossier du lanceur."""
    expected = Path(desktop.__file__).resolve().parent / "static/mastermind.svg"
    assert desktop.resource_path("static/mastermind.svg") == expected


def test_configure_qt_identity_reuses_application(monkeypatch: pytest.MonkeyPatch) -> None:
    """L'identité Qt est appliquée à l'application graphique existante."""
    qt_app = MagicMock(spec=QApplication)
    monkeypatch.setattr(QApplication, "instance", staticmethod(lambda: qt_app))
    assert desktop.configure_qt_identity() is qt_app
    qt_app.setApplicationName.assert_called_once_with(desktop.APP_NAME)
    qt_app.setWindowIcon.assert_called_once()


def test_window_starts_game_and_manages_guess(window: desktop.MastermindWindow) -> None:
    """La fenêtre crée une partie et permet d'ajouter ou retirer des choix."""
    window.start_game()
    value = MODES[window.selected_mode()]["choices"][0]["value"]
    window.add_choice(value)
    window.add_choice(value)
    assert window.guess == [value, value]
    window.remove_choice(0)
    assert window.guess == [value]
    window.clear_guess()
    assert window.guess == []


def test_window_rejects_incomplete_guess(window: desktop.MastermindWindow) -> None:
    """Une proposition incomplète affiche une aide sans appeler le moteur."""
    window.start_game()
    window.validate_current_guess()
    assert "quatre valeurs" in window.message.text()


def test_window_submits_winning_guess(
    window: desktop.MastermindWindow, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Une combinaison complète peut gagner depuis l'interface native."""
    window.start_game()
    assert window.game is not None
    stored = storage.get_game(window.game["id"])
    assert stored is not None
    window.guess = list(stored["secret"])
    information = MagicMock()
    monkeypatch.setattr(QMessageBox, "information", information)
    window.validate_current_guess()
    assert window.game is not None
    assert window.game["status"] == "won"
    information.assert_called_once()


def test_window_formats_easy_feedback(window: desktop.MastermindWindow) -> None:
    """Le mode enfant décrit chaque indice de tentative."""
    attempt: Attempt = {
        "number": 1, "guess": ["1", "2", "3", "4"], "well_placed": 1,
        "misplaced": 1, "result": "11",
        "feedback": ["well_placed", "misplaced", "absent", "absent"],
        "created_at": "2026-01-01T00:00:00+00:00",
    }
    window.difficulty.setCurrentIndex(window.difficulty.findData("easy"))
    text = window._attempt_text(attempt)
    assert "bien placé" in text
    assert "mal placé" in text
    assert "absent" in text


def test_window_abandons_active_game(window: desktop.MastermindWindow) -> None:
    """Le bouton d'abandon termine une partie active."""
    window.start_game()
    window.abandon_game()
    assert window.game is not None
    assert window.game["status"] == "lost"


def test_run_executes_native_application(monkeypatch: pytest.MonkeyPatch) -> None:
    """Le point d'entrée initialise SQLite et exécute uniquement Qt."""
    qt_app = MagicMock(spec=QApplication)
    qt_app.exec.return_value = 0
    native_window = MagicMock()
    monkeypatch.setattr(desktop, "init_db", MagicMock())
    monkeypatch.setattr(desktop, "configure_qt_identity", MagicMock(return_value=qt_app))
    monkeypatch.setattr(desktop, "MastermindWindow", MagicMock(return_value=native_window))
    with pytest.raises(SystemExit, match="0"):
        desktop.run()
    native_window.show.assert_called_once()
