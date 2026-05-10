import logging
from PyQt6 import QtWidgets

from exceptions.file_exceptions import FileLoadError


def center_on_screen(widget):
    screen = QtWidgets.QApplication.primaryScreen()

    if not screen:
        return

    screen_geometry = screen.availableGeometry()
    x = (screen_geometry.width() - widget.width()) // 2
    y = (screen_geometry.height() - widget.height()) // 2
    widget.move(x, y)


def apply_style(widget, style_path):
    try:
        with open(style_path, "r") as f:
            widget.setStyleSheet(f.read())

    except FileNotFoundError as e:
        logging.exception(f"Style file not found: {style_path}")
        raise FileLoadError(f"Style file missing: {style_path}") from e

    except Exception as e:
        logging.exception(f"Failed to apply style from {style_path}")
        raise FileLoadError(f"Failed to load style: {style_path}") from e


def apply_qss_with_image(widget, qss_file_path, image_path):
    try:
        with open(qss_file_path, "r") as f:
            qss = f.read()

        qss = qss.replace("CHECKMARK_IMAGE", image_path.replace("\\", "/"))
        widget.setStyleSheet(qss)

    except FileNotFoundError as e:
        logging.exception(f"QSS file not found: {qss_file_path}")
        raise FileLoadError(f"QSS file missing: {qss_file_path}") from e

    except Exception as e:
        logging.exception(f"Failed to apply QSS: {qss_file_path}")
        raise FileLoadError(f"Failed to load QSS: {qss_file_path}") from e