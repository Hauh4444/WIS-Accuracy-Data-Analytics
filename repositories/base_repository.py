import pyodbc
import logging
import pandas as pd

from exceptions.database_exceptions import DatabaseConnectionError, DatabaseQueryError, DatabaseInsertError, DatabaseUpdateError


class BaseRepository:

    def __init__(self, connection):
        self.connection = connection

    def _read(self, query, params=None):
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, params or [])

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            return pd.DataFrame.from_records(rows, columns=columns)

        except pyodbc.Error as e:
            logging.exception("Database read/query failed")
            raise DatabaseQueryError(str(e)) from e

        finally:
            cursor.close()

    def _execute(self, query, params=None):
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, params or [])

            self.connection.commit()

        except pyodbc.IntegrityError as e:
            self.connection.rollback()
            logging.exception("Database insert/update integrity error")
            raise DatabaseInsertError(str(e)) from e

        except pyodbc.ProgrammingError as e:
            self.connection.rollback()
            logging.exception("Database update/query programming error")
            raise DatabaseUpdateError(str(e)) from e

        except pyodbc.Error as e:
            self.connection.rollback()
            logging.exception("Database execute failed")
            raise DatabaseQueryError(str(e)) from e

        finally:
            cursor.close()

    def _executemany(self, query, params_list):
        cursor = self.connection.cursor()

        try:
            cursor.executemany(query, params_list)

            self.connection.commit()

        except pyodbc.IntegrityError as e:
            self.connection.rollback()
            logging.exception("Database batch insert integrity error")
            raise DatabaseInsertError(str(e)) from e

        except pyodbc.Error as e:
            self.connection.rollback()
            logging.exception("Database batch execute failed")
            raise DatabaseQueryError(str(e)) from e

        finally:
            cursor.close()

    def _exists(self, query, params=None):
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, params or [])

            return cursor.fetchone() is not None

        except pyodbc.Error as e:
            logging.exception("Database exists check failed")
            raise DatabaseQueryError(str(e)) from e

        finally:
            cursor.close()