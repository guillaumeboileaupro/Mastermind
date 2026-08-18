import sys
from functools import partial
from pathlib import Path

from fastapi import HTTPException
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QMainWindow, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from app.game import CODE_LENGTH, MODES
from app.main import (
    GuessRequest, NewGameRequest, current_game, give_up, history, new_game,
    stats, submit_guess,
)
from app.storage import init_db
from app.types import Attempt, PublicGame

APP_NAME = "Mastermind"
DESKTOP_APP_ID = "mastermind"


def resource_path(relative: str) -> Path:
    """Résout une ressource embarquée depuis la racine du projet."""
    return Path(__file__).resolve().parent / relative


def configure_qt_identity() -> QApplication:
    """Crée ou configure l'application Qt native avec l'identité Mastermind."""
    instance = QApplication.instance()
    if instance is None:
        qt_app = QApplication(sys.argv)
    elif isinstance(instance, QApplication):
        qt_app = instance
    else:
        raise RuntimeError("Une application Qt incompatible est déjà active")
    qt_app.setApplicationName(APP_NAME)
    qt_app.setApplicationDisplayName(APP_NAME)
    qt_app.setDesktopFileName(DESKTOP_APP_ID)
    qt_app.setOrganizationName("Guillaume Boileau")
    qt_app.setWindowIcon(QIcon(str(resource_path("static/mastermind.svg"))))
    return qt_app


class MastermindWindow(QMainWindow):
    """Fenêtre PyQt6 native qui pilote une partie de Mastermind."""

    def __init__(self) -> None:
        """Construit les contrôles, restaure la partie et démarre l'horloge."""
        super().__init__()
        self.game: PublicGame | None = None
        self.guess: list[str] = []
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(900, 700)
        self.mode = QComboBox()
        for key, config in MODES.items():
            self.mode.addItem(config["label"], key)
        self.difficulty = QComboBox()
        self.difficulty.addItem("Normal", "normal")
        self.difficulty.addItem("Facile enfant", "easy")
        self.message = QLabel("Choisis un mode et démarre une partie.")
        self.timer_label = QLabel("00:00")
        self.current_score = QLabel("0")
        self.total_score = QLabel("0")
        self.wins = QLabel("0/0")
        self.guess_layout = QHBoxLayout()
        self.palette_layout = QHBoxLayout()
        self.attempts_layout = QVBoxLayout()
        self.history_table = QTableWidget(0, 6)
        self.history_table.setHorizontalHeaderLabels(
            ["Mode", "Résultat", "Essais", "Temps", "Score", "Code"]
        )
        self._build_layout()
        self.mode.currentIndexChanged.connect(self.render_palette)
        self.difficulty.currentIndexChanged.connect(self.render_attempts)
        self.clock = QTimer(self)
        self.clock.timeout.connect(self.update_clock)
        self.clock.start(1000)
        self.refresh_all()

    def _build_layout(self) -> None:
        """Assemble les widgets natifs dans la fenêtre principale."""
        root = QWidget()
        page = QVBoxLayout(root)
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Mode"))
        controls.addWidget(self.mode)
        controls.addWidget(QLabel("Difficulté"))
        controls.addWidget(self.difficulty)
        new_button = QPushButton("Nouvelle partie")
        new_button.clicked.connect(self.start_game)
        controls.addWidget(new_button)
        give_up_button = QPushButton("Abandonner")
        give_up_button.clicked.connect(self.abandon_game)
        controls.addWidget(give_up_button)
        page.addLayout(controls)
        score_box = QGridLayout()
        for column, (title, widget) in enumerate((
            ("Temps", self.timer_label), ("Score actuel", self.current_score),
            ("Score total", self.total_score), ("Victoires", self.wins),
        )):
            score_box.addWidget(QLabel(title), 0, column)
            score_box.addWidget(widget, 1, column)
        page.addLayout(score_box)
        game_box = QGroupBox("Combinaison")
        game_layout = QVBoxLayout(game_box)
        game_layout.addLayout(self.guess_layout)
        game_layout.addLayout(self.palette_layout)
        actions = QHBoxLayout()
        clear_button = QPushButton("Tout effacer")
        clear_button.clicked.connect(self.clear_guess)
        submit_button = QPushButton("Valider")
        submit_button.clicked.connect(self.validate_current_guess)
        actions.addWidget(clear_button)
        actions.addWidget(submit_button)
        game_layout.addLayout(actions)
        game_layout.addWidget(self.message)
        page.addWidget(game_box)
        attempts_box = QGroupBox("Tentatives")
        attempts_box.setLayout(self.attempts_layout)
        page.addWidget(attempts_box)
        page.addWidget(QLabel("Historique des parties"))
        page.addWidget(self.history_table)
        self.setCentralWidget(root)

    @staticmethod
    def _clear_layout(layout: QHBoxLayout | QVBoxLayout) -> None:
        """Supprime tous les widgets contenus dans une disposition Qt."""
        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def selected_mode(self) -> str:
        """Retourne l'identifiant du mode sélectionné."""
        return str(self.mode.currentData())

    def is_easy_mode(self) -> bool:
        """Indique si les indices détaillés pour enfant sont activés."""
        return bool(self.difficulty.currentData() == "easy")

    def start_game(self) -> None:
        """Crée une partie dans le mode sélectionné et rafraîchit la fenêtre."""
        self.game = new_game(NewGameRequest(mode=self.selected_mode()))
        self.guess = []
        self.message.setText("Trouve la combinaison secrète.")
        self.refresh_all()

    def abandon_game(self) -> None:
        """Abandonne la partie active après vérification de son existence."""
        if self.game is None or self.game["status"] != "active":
            return
        self.game = give_up(self.game["id"])
        self.message.setText("Partie abandonnée.")
        self.refresh_all()

    def add_choice(self, value: str) -> None:
        """Ajoute une valeur si la proposition dispose encore d'une place."""
        if self.game is not None and self.game["status"] == "active" and len(self.guess) < CODE_LENGTH:
            self.guess.append(value)
            self.render_guess()

    def remove_choice(self, index: int) -> None:
        """Retire la valeur située à l'index demandé."""
        if 0 <= index < len(self.guess):
            self.guess.pop(index)
            self.render_guess()

    def clear_guess(self) -> None:
        """Vide entièrement la proposition en cours."""
        self.guess = []
        self.render_guess()

    def validate_current_guess(self) -> None:
        """Soumet une proposition complète et affiche son nouvel état."""
        if self.game is None or len(self.guess) != CODE_LENGTH:
            self.message.setText("Choisis quatre valeurs avant de valider.")
            return
        try:
            self.game = submit_guess(self.game["id"], GuessRequest(guess=list(self.guess)))
        except HTTPException as error:
            self.message.setText(str(error.detail))
            return
        self.guess = []
        if self.game["status"] == "won":
            QMessageBox.information(self, "Victoire", "Combinaison trouvée !")
        self.refresh_all()

    def render_palette(self) -> None:
        """Affiche les boutons correspondant aux choix du mode sélectionné."""
        self._clear_layout(self.palette_layout)
        selected = self.selected_mode()
        for choice in MODES[selected]["choices"]:
            button = QPushButton(choice["label"])
            if selected == "colors":
                button.setStyleSheet(f"background-color: {choice['value']}; min-height: 44px;")
            button.clicked.connect(partial(self.add_choice, choice["value"]))
            self.palette_layout.addWidget(button)

    def render_guess(self) -> None:
        """Affiche les quatre positions de la proposition courante."""
        self._clear_layout(self.guess_layout)
        for index in range(CODE_LENGTH):
            value = self.guess[index] if index < len(self.guess) else None
            button = QPushButton(value or "?")
            if value and self.selected_mode() == "colors":
                button.setText("")
                button.setStyleSheet(f"background-color: {value}; min-height: 52px;")
            if value:
                button.clicked.connect(partial(self.remove_choice, index))
            self.guess_layout.addWidget(button)

    def render_attempts(self) -> None:
        """Affiche les tentatives et les indices détaillés du mode facile."""
        self._clear_layout(self.attempts_layout)
        attempts = self.game["attempts"] if self.game else []
        if not attempts:
            self.attempts_layout.addWidget(QLabel("Aucune tentative."))
            return
        for attempt in reversed(attempts):
            self.attempts_layout.addWidget(QLabel(self._attempt_text(attempt)))

    def _attempt_text(self, attempt: Attempt) -> str:
        """Formate une tentative avec ses indices éventuels."""
        values = " · ".join(self._choice_label(value) for value in attempt["guess"])
        text = f"#{attempt['number']}  {values}  → {attempt['result']}"
        if self.is_easy_mode() and "feedback" in attempt:
            labels = {"well_placed": "✓ bien placé", "misplaced": "↔ mal placé", "absent": "✕ absent"}
            text += "  |  " + ", ".join(labels[item] for item in attempt["feedback"])
        return text

    def _choice_label(self, value: str, mode: str | None = None) -> str:
        """Retrouve le libellé humain d'une valeur de jeu."""
        selected = mode or (self.game["mode"] if self.game else self.selected_mode())
        for choice in MODES[selected]["choices"]:
            if choice["value"] == value:
                return choice["label"]
        return value

    def update_clock(self) -> None:
        """Actualise le chronomètre et le score provisoire."""
        if self.game is None:
            return
        refreshed = current_game() if self.game["status"] == "active" else self.game
        if refreshed is not None:
            self.game = refreshed
        seconds = self.game["elapsed_seconds"]
        self.timer_label.setText(f"{seconds // 60:02d}:{seconds % 60:02d}")
        self.current_score.setText(str(self.game["current_score"]))

    def render_history(self) -> None:
        """Recharge les statistiques et les parties terminées depuis SQLite."""
        game_stats = stats()
        self.total_score.setText(str(game_stats["total_score"]))
        self.wins.setText(f"{game_stats['wins']}/{game_stats['games_total']}")
        games = history(50)
        self.history_table.setRowCount(len(games))
        for row, game in enumerate(games):
            secret = " · ".join(self._choice_label(value, game["mode"]) for value in game["secret"] or [])
            values = (MODES[game["mode"]]["label"], game["status"], str(len(game["attempts"])),
                      f"{game['elapsed_seconds'] // 60:02d}:{game['elapsed_seconds'] % 60:02d}",
                      str(game["score"]), secret)
            for column, value in enumerate(values):
                self.history_table.setItem(row, column, QTableWidgetItem(value))

    def refresh_all(self) -> None:
        """Synchronise tous les éléments avec l'état persistant."""
        if self.game is None:
            self.game = current_game()
        if self.game is not None:
            self.mode.setCurrentIndex(self.mode.findData(self.game["mode"]))
        self.render_palette()
        self.render_guess()
        self.render_attempts()
        self.render_history()
        self.update_clock()


def run() -> None:
    """Initialise SQLite et exécute l'application desktop PyQt6 native."""
    init_db()
    qt_app = configure_qt_identity()
    window = MastermindWindow()
    window.show()
    raise SystemExit(qt_app.exec())


if __name__ == "__main__":
    run()
