import sqlite3

from pydantic import validate_call


class SQLiteWrapper:
    """
    Wrapper for SQLite3 implementing the context manager pattern
    to manage opening and closing connections

    Attributes:
    db_path: str path to db disk file
    """

    @validate_call
    def __init__(self, db_path: str) -> None:
        """
        Initialize the SQLiteWrapper object, set the db_path and
        set the SQLITE_JOURNAL_MODE to WAL to improve performance

        @type db_path: str
        @param db_path: path to db disk file
        """
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute("PRAGMA journal_mode=WAL;")
        self.connection.close()
        self.connection = None

    def __enter__(self):
        """
        Open the connection to the db
        """
        self.connection = sqlite3.connect(self.db_path)

        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close the connection to the db if it exists
        """
        if self.connection:
            self.connection.commit()
            self.connection.close()
            self.connection = None
