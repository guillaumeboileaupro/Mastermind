import os
import socket
import sys
import threading
import time
from pathlib import Path

import uvicorn
import webview
from PyQt6.QtWidgets import QApplication

from app.main import app

APP_NAME = "Mastermind"
DESKTOP_APP_ID = "mastermind"
HOST = "127.0.0.1"


def resource_path(relative: str) -> Path:
    """Résout le chemin d'une ressource embarquée depuis la racine du projet."""
    return Path(__file__).resolve().parent / relative


def find_free_port() -> int:
    """Demande au système un port TCP local actuellement disponible."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, 0))
        return int(sock.getsockname()[1])


def wait_for_server(port: int, timeout: float = 10.0) -> None:
    """Attend que le serveur local accepte les connexions ou lève une erreur."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex((HOST, port)) == 0:
                return
        time.sleep(0.05)
    raise RuntimeError("Le serveur local Mastermind n'a pas démarré")


def configure_qt_identity() -> QApplication:
    """Force l'identité affichée par Ubuntu/Qt au lieu du nom desktop.py."""
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
    return qt_app


def run() -> None:
    """Démarre l'API locale et ouvre la fenêtre desktop pywebview."""
    # pywebview/Qt réutilise cette QApplication existante et conserve son identité.
    configure_qt_identity()

    port = find_free_port()
    config = uvicorn.Config(
        app,
        host=HOST,
        port=port,
        log_level="warning",
        access_log=False,
        loop="asyncio",
        http="h11",
        ws="none",
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, name="mastermind-api", daemon=True)
    thread.start()
    wait_for_server(port)

    data_home = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    webview_storage = data_home / "mastermind" / "webview"
    webview_storage.mkdir(parents=True, exist_ok=True)

    webview.create_window(
        APP_NAME,
        f"http://{HOST}:{port}",
        width=1180,
        height=820,
        min_size=(760, 620),
        resizable=True,
        background_color="#f3f6fb",
    )
    try:
        webview.start(
            gui="qt",
            icon=str(resource_path("static/mastermind.svg")),
            private_mode=False,
            storage_path=str(webview_storage),
        )
    finally:
        server.should_exit = True
        thread.join(timeout=2)


if __name__ == "__main__":
    run()
