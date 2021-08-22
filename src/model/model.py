import inspect
from src import database


class Model:
    db = database.mysql.MySQL()
    db_vars = []
    table_name = None

    def __init__(self):
        pass

    @classmethod
    def __init__from_db(cls, *args, **kwargs):
        instance = cls.__init__(*args, **kwargs)
        instance.load()

    @classmethod
    def create(cls):
        pass

    @classmethod
    def load(cls, filters: list[database.DatabaseFilter] = None, count=0):
        db_models = cls.db.load(cls.table_name, filters)
        models = []
        for db_model in db_models:
            model = cls()
            for db_var in cls.db_vars:
                setattr(model, db_var, db_model[db_var])
            models.append(model)
        return models

    def get_database_entries(self):
        database_entries = []
        attributes = inspect.getmembers(self, lambda a: not (inspect.isroutine(a)))
        for attribute in attributes:
            if attribute[0] in self.db_vars:
                db_entry = database.DatabaseEntry(attribute[0], attribute[1])
                database_entries.append(db_entry)
        return database_entries

    def save(self):
        self.db.save(self.table_name, self.get_database_entries())

