import os
from unittest.mock import MagicMock
from PyQt6 import QtWidgets
import pytest

from utils import center_on_screen, apply_style


def test_center_on_screen_moves_widget(monkeypatch):
    widget = MagicMock()
    widget.width.return_value = 100
    widget.height.return_value = 50

    rect_mock = MagicMock()
    rect_mock.width.return_value = 800
    rect_mock.height.return_value = 600

    screen_mock = MagicMock()
    screen_mock.availableGeometry.return_value = rect_mock

    monkeypatch.setattr(QtWidgets.QApplication, "primaryScreen", lambda: screen_mock)

    center_on_screen(widget)

    widget.move.assert_called_once()
    x, y = widget.move.call_args[0]
    assert x == (800 - 100) // 2
    assert y == (600 - 50) // 2


def test_center_on_screen_no_screen(monkeypatch):
    widget = MagicMock()
    monkeypatch.setattr(QtWidgets.QApplication, "primaryScreen", lambda: None)

    # Should not raise
    center_on_screen(widget)
    widget.move.assert_not_called()


def test_apply_style_reads_file(tmp_path):
    widget = MagicMock()
    style_file = tmp_path / "style.qss"
    style_file.write_text("QWidget { background-color: red; }")

    apply_style(widget, str(style_file))
    widget.setStyleSheet.assert_called_once_with("QWidget { background-color: red; }")


def test_apply_style_file_not_found(monkeypatch):
    widget = MagicMock()
    fake_path = "nonexistent.qss"

    monkeypatch.setattr(os.path, "exists", lambda path: False)

    apply_style(widget, fake_path)
    widget.setStyleSheet.assert_not_called()


def test_apply_style_exception(monkeypatch, tmp_path):
    widget = MagicMock()
    style_file = tmp_path / "style.qss"
    style_file.write_text("QWidget { background-color: red; }")

    def fake_open(*args, **kwargs):
        raise IOError("read error")

    monkeypatch.setattr("builtins.open", fake_open)

    apply_style(widget, str(style_file))
    widget.setStyleSheet.assert_not_called()
