import MySQLdb
import os
from . import entry
from . import filter
from . import column
from . import database
import authenticator


class MySQL(database.Database):

    none_db_value = "NULL"

    username = os.getenv('DB_USERNAME') if 'DB_USERNAME' in os.environ else authenticator.DB_USERNAME
    password = os.getenv('DB_PASSWORD') if 'DB_PASSWORD' in os.environ else authenticator.DB_PASSWORD
    host = os.getenv('DB_HOST') if 'DB_HOST' in os.environ else authenticator.DB_HOST
    name = os.getenv('DB_NAME') if 'DB_NAME' in os.environ else authenticator.DB_NAME

    def __init__(self):
        super().__init__()
        self.db = None
        self.connect_db()

    def connect_db(self):
        self.db = MySQLdb.connect(
            host=self.host,
            user=self.username,
            passwd=self.password,
            database=self.name,
            charset="utf8mb4")

    def get_cursor(self):
        return self.db.cursor(MySQLdb.cursors.DictCursor)

    def save(self, table_name, entries: list[entry.DatabaseEntry], update=True):
        query = f"INSERT INTO {table_name}"

        insert_column_str = "("
        for entry in entries:
            insert_column_str += entry.column + ","
        insert_column_str = insert_column_str[:-1]
        insert_column_str += ")"

        insert_value_str = "("
        for entry in entries:
            if entry.value is None:
                value = self.none_db_value
            else:
                value = "\"" + entry.value + "\""
            insert_value_str += str(value) + ","
        insert_value_str = insert_value_str[:-1]
        insert_value_str += ")"

        query += f" {insert_column_str} VALUES {insert_value_str}"

        # NOTE comma at the end may not work
        if update:
            key_update_str = " ON DUPLICATE KEY UPDATE"
            for entry in entries:
                if entry.value is None:
                    value = self.none_db_value
                else:
                    value = "\"" + entry.value + "\""
                key_update_str += f" {entry.column}=VALUES({entry.column}),"
            key_update_str = key_update_str[:-1]
            query += key_update_str
        cursor = self.get_cursor()
        cursor.execute(query)
        self.db.commit()

    def load(self, table_name, filters: list[filter.DatabaseFilter]):
        query = f"SELECT * FROM {table_name}"

        if filters and len(filters) >= 1:
            db_filter = filters[0]
            query += f" WHERE {db_filter.column} {db_filter.equality} {db_filter.value}"

            for i in range(1, len(filters)):
                query += f" AND {db_filter.column} {db_filter.equality} {db_filter.value}"

        cursor = self.get_cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def create(self, table_name, columns: list[column.DatabaseColumn]):
        query = f"CREATE TABLE {table_name}"
        column_str = "("
        for column in columns:
            column_str += f"{column.name} {column.details},"

        primary_key_str = "PRIMARY KEY("
        for column in columns:
            if column.primary:
                primary_key_str += column.name + ","
        primary_key_str = primary_key_str[:-1]
        primary_key_str += ")"

        column_str += primary_key_str
        column_str += ")"

        query += column_str

        cursor = self.get_cursor()
        cursor.execute(query)

    def create_db(self):
        query = f'CREATE DATABASE {self.name} CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;'
        cursor = self.get_cursor()
        cursor.execute(query)
