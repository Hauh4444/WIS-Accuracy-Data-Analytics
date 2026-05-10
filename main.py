import sys
import logging
from PyQt6 import QtWidgets

from bootstrap.container import AppContainer
from controllers.application_controller import ApplicationController
from utils.logging import setup_logging


if __name__ == "__main__":
    setup_logging()

    try:
        app = QtWidgets.QApplication(sys.argv)
        container = AppContainer()
        controller = ApplicationController(container)
        controller.run()

        if controller.window:
            sys.exit(app.exec())

        sys.exit(0)

    except Exception:
        logging.exception("Unhandled application error")