from . import entry
from . import filter
from . import column


class Database:

    none_db_value = ""

    def __init__(self):
        pass

    def save(self, table_name, entries: list[entry.DatabaseEntry]):
        pass

    def load(self, table_name, filters: list[filter.DatabaseFilter]):
        pass

    def create(self, table_name, columns: list[column.DatabaseColumn]):
        pass

    def create_db(self):
        pass
