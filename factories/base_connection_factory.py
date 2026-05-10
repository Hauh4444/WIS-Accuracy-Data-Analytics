import pyodbc
import logging
from pathlib import Path

from exceptions.database_exceptions import DatabaseConnectionError


class BaseConnectionFactory:

    DRIVER = r"Microsoft Access Driver (*.mdb, *.accdb)"

    def _connect(self, db_path: str) -> pyodbc.Connection:
        try:
            if not db_path:
                raise DatabaseConnectionError("Database path is empty or invalid")

            if not Path(db_path).exists():
                raise DatabaseConnectionError(f"Database not found: {db_path}")

            conn_str = (
                rf"DRIVER={{{self.DRIVER}}};"
                rf"DBQ={db_path};"
            )

            return pyodbc.connect(conn_str, autocommit=False)

        except pyodbc.Error as e:
            logging.exception("ODBC connection failure")
            raise DatabaseConnectionError("Failed to connect to database") from e

        except Exception as e:
            logging.exception("Unexpected database connection error")
            raise DatabaseConnectionError("Unexpected database connection failure") from e