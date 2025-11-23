from unittest.mock import MagicMock
from PyQt6 import QtWidgets
from utils import center_on_screen, apply_style


def test_center_on_screen_moves_widget(monkeypatch):
    widget = MagicMock()
    widget.width.return_value = 100
    widget.height.return_value = 50

    screen_mock = MagicMock()
    screen_mock.availableGeometry.return_value.width.return_value = 800
    screen_mock.availableGeometry.return_value.height.return_value = 600

    monkeypatch.setattr(QtWidgets.QApplication, "primaryScreen", lambda: screen_mock)

    center_on_screen(widget)

    widget.move.assert_called_once()
    x, y = widget.move.call_args[0]
    assert x == (screen_mock.availableGeometry.return_value.width.return_value - 100) // 2
    assert y == (screen_mock.availableGeometry.return_value.height.return_value - 50) // 2


def test_center_on_screen_no_screen(monkeypatch):
    widget = MagicMock()
    monkeypatch.setattr(QtWidgets.QApplication, "primaryScreen", lambda: None)

    center_on_screen(widget)


def test_apply_style_reads_file(tmp_path):
    widget = MagicMock()
    style_file = tmp_path / "style.qss"
    style_file.write_text("QWidget { background-color: red; }")

    apply_style(widget, str(style_file))
    widget.setStyleSheet.assert_called_once_with("QWidget { background-color: red; }")


def test_apply_style_file_not_found():
    widget = MagicMock()
    apply_style(widget, "nonexistent.qss")


def test_apply_style_exception(monkeypatch, tmp_path):
    widget = MagicMock()
    style_file = tmp_path / "style.qss"
    style_file.write_text("QWidget { background-color: red; }")

    def fake_open(*args, **kwargs):
        raise IOError("read error")
    monkeypatch.setattr("builtins.open", fake_open)

    apply_style(widget, str(style_file))