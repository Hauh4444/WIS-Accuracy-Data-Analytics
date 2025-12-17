import logging
from PyQt6 import QtWidgets


def center_on_screen(widget: QtWidgets.QWidget) -> None:
    """Center a widget on the primary screen.

    Args:
        widget: QtWidget to center on screen
    """
    screen = QtWidgets.QApplication.primaryScreen()
    if not screen: return
    screen_geometry = screen.availableGeometry()
    x = (screen_geometry.width() - widget.width()) // 2
    y = (screen_geometry.height() - widget.height()) // 2
    widget.move(x, y)


def apply_style(widget: QtWidgets.QWidget, style_path: str) -> None:
    """Apply stylesheet to QtWidget.

    Args:
        widget: QtWidget to apply style to
        style_path: String path of the qss stylesheet
    """
    try:
        with open(style_path, "r") as f:
            widget.setStyleSheet(f.read())
    except Exception as e:
        logging.warning(f"Could not apply style from {style_path}: {e}")