from typing import Tuple

from .db import SQLiteWrapper

import time

import json


class SessionCache:
    """
    A simple session cache that uses sqlite to simulate a caching
    database

    Attributes:
    db_path: str path to db disk file
    db: SQLiteWrapper connection to local db
    ttl: int time to live for database entry in milliseconds
    """

    def __init__(self, db_path: str, ttl: int = 60000) -> None:
        """
        Initialize the SessionCache object with a database connection
        and create a table to cache results

        @type db_path: str
        @type ttl: int
        @param db_path: path to db disk file
        @param ttl: time to live for database entry in milliseconds,
        defaulting to 1 minute
        """

        self.db_path = db_path
        self.db = SQLiteWrapper(self.db_path)
        self.time_to_live = ttl
        self.__create_cache_table()

    def __create_cache_table(self) -> None:
        """
        Private function to create the cache table if it doesn't exist
        """

        with self.db as conn:
            cursor = conn.cursor()
            query = """
        CREATE TABLE IF NOT EXISTS cache (
          query TEXT,
          variables TEXT,
          user TEXT DEFAULT '',
          data BLOB,
          expiry_time INTEGER,
          version INTEGER,
          PRIMARY KEY (query, variables, user)
        )
      """

            cursor.execute(query)

    def get(
        self, query: str, variables: dict, user: str | None, version: int
    ) -> Tuple | None:
        """
        Get the data from the cache for the given url and query. If the
        queried result is expired or has an invalid version number, all
        invalid database entries are deleted and the function returns None

        @type query: str
        @type variables: dict
        @type user: str | None
        @type version: int
        @param query: fetch request graphQL query
        @param variables: dictionary containing graphQL variables
        @param user: username of logged in user (or None)
        @param version: number denoting version since last data mutation
        @rtype: Tuple | None
        @returns: the data if it exists, otherwise None
        """

        with self.db as conn:
            cursor = conn.cursor()
            sql_query = """
        SELECT * FROM cache WHERE
          query = ? AND
          variables = ? AND
          user = ?
      """

            cursor.execute(
                sql_query, (query, json.dumps(variables), user if user else "")
            )

            result = cursor.fetchone()

            if result:
                expired = round(time.time() * 1000) > result[4]
                unmatching_version = result[5] != version
                if expired or unmatching_version:
                    delete_query = """
            DELETE FROM cache WHERE
              expiry_time <= ? OR 
              version != ?
          """
                    cursor.execute(delete_query, (round(time.time() * 1000), version))
                else:
                    return result

    def set(
        self, query: str, variables: dict, user: str | None, data: str, version: int
    ) -> bool:
        """
        Set the data in the cache for the given url and query if it does not
        already exist.

        @type query: str
        @type variables: dict
        @type user: str | None
        @type data: str
        @type version: int
        @param query: fetch request graphQL query
        @param variables: dictionary containing graphQL variables
        @param user: username of logged in user (or None)
        @param data: data to be cached
        @param version: number denoting version since last data mutation
        @rtype: bool
        @returns: True if the data was set, False if the data already exists
        """

        if self.get(query, variables, user, version) is not None:
            return False

        with self.db as conn:
            cursor = conn.cursor()
            sql_query = """
        INSERT INTO cache VALUES (?, ?, ?, ?, ?, ?)
      """
            expiry_time = round(time.time() * 1000) + self.time_to_live

            cursor.execute(
                sql_query,
                (
                    query,
                    json.dumps(variables),
                    user if user else "",
                    json.dumps(data),
                    expiry_time,
                    version,
                ),
            )

        return True
