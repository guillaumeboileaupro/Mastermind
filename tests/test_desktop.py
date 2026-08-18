import socket
import threading
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import uvicorn
import webview
from PyQt6.QtWidgets import QApplication

import desktop


def test_resource_path_is_relative_to_desktop_module() -> None:
    """Les ressources sont résolues depuis le dossier du lanceur."""
    expected = Path(desktop.__file__).resolve().parent / "static/mastermind.svg"

    assert desktop.resource_path("static/mastermind.svg") == expected


def test_find_free_port_returns_bindable_local_port() -> None:
    """Le port proposé peut être réservé sur l'interface locale."""
    port = desktop.find_free_port()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((desktop.HOST, port))


def test_wait_for_server_detects_listening_socket() -> None:
    """L'attente se termine lorsqu'un serveur écoute sur le port demandé."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((desktop.HOST, 0))
        server.listen()
        port = int(server.getsockname()[1])

        desktop.wait_for_server(port, timeout=0.2)


def test_wait_for_server_times_out() -> None:
    """L'attente signale clairement un serveur qui ne démarre pas."""
    port = desktop.find_free_port()

    with pytest.raises(RuntimeError, match="n'a pas démarré"):
        desktop.wait_for_server(port, timeout=0.01)


def test_configure_qt_identity_reuses_application(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """L'identité Qt est appliquée à l'application graphique existante."""
    qt_app = MagicMock(spec=QApplication)
    monkeypatch.setattr(QApplication, "instance", staticmethod(lambda: qt_app))

    configured = desktop.configure_qt_identity()

    assert configured is qt_app
    qt_app.setApplicationName.assert_called_once_with(desktop.APP_NAME)
    qt_app.setApplicationDisplayName.assert_called_once_with(desktop.APP_NAME)
    qt_app.setDesktopFileName.assert_called_once_with(desktop.DESKTOP_APP_ID)
    qt_app.setOrganizationName.assert_called_once_with("Guillaume Boileau")


def test_run_starts_and_stops_desktop_components(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Le lanceur orchestre le serveur, la fenêtre et leur arrêt propre."""
    server = MagicMock()
    server.run.return_value = None
    server.should_exit = False
    thread = MagicMock(spec=threading.Thread)
    config = MagicMock()
    create_window = MagicMock()
    start_webview = MagicMock()
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.setattr(desktop, "configure_qt_identity", MagicMock())
    monkeypatch.setattr(desktop, "find_free_port", lambda: 8765)
    monkeypatch.setattr(desktop, "wait_for_server", lambda port: None)
    monkeypatch.setattr(uvicorn, "Config", MagicMock(return_value=config))
    monkeypatch.setattr(uvicorn, "Server", MagicMock(return_value=server))
    monkeypatch.setattr(threading, "Thread", MagicMock(return_value=thread))
    monkeypatch.setattr(webview, "create_window", create_window)
    monkeypatch.setattr(webview, "start", start_webview)

    desktop.run()

    create_window.assert_called_once()
    start_webview.assert_called_once()
    thread.start.assert_called_once()
    thread.join.assert_called_once_with(timeout=2)
    assert server.should_exit is True
