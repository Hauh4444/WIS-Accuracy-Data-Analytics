import logging

from factories.base_connection_factory import BaseConnectionFactory
from exceptions.database_exceptions import DatabaseConnectionError


class WisdomConnectionFactory(BaseConnectionFactory):

    def __init__(self, db_path: str):
        if not db_path:
            raise DatabaseConnectionError("Wisdom database path is empty")

        self.db_path = db_path

    def create(self):
        try:
            return self._connect(self.db_path)

        except DatabaseConnectionError:
            raise

        except Exception as e:
            logging.exception("Failed to create Wisdom database connection")
            raise DatabaseConnectionError("Wisdom database connection failed") from e