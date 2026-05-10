import logging

from factories.base_connection_factory import BaseConnectionFactory
from utils.paths import get_db_path
from exceptions.database_exceptions import DatabaseConnectionError


class LocalConnectionFactory(BaseConnectionFactory):

    def __init__(self):
        try:
            self.db_path = get_db_path()

        except Exception as e:
            logging.exception("Failed to resolve local database path")
            raise DatabaseConnectionError("Failed to locate database file") from e

    def create(self):
        try:
            return self._connect(str(self.db_path))

        except DatabaseConnectionError:
            raise

        except Exception as e:
            logging.exception("Failed to create database connection")
            raise DatabaseConnectionError("Database connection failed") from e