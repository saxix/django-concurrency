# from django.db.backends.sqlite3.base import *
from django.db.backends.sqlite3.base import DatabaseWrapper as Sqlite3DatabaseWrapper
from concurrency.db.backends.sqlite3.creation import Sqlite3Creation


class DatabaseWrapper(Sqlite3DatabaseWrapper):
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.creation = Sqlite3Creation(self)

    def _clone(self):
        return self.__class__(self.settings_dict, self.alias)

    def list_triggers(self):
        cursor = self.cursor()
        result = cursor.execute("select name from sqlite_master where type = 'trigger';")
        return [m[0] for m in result.fetchall()]

    def drop_trigger(self, trigger_name):
        cursor = self.cursor()
        result = cursor.execute("DROP TRIGGER IF EXISTS %s;" % trigger_name)
        return result

    def drop_triggers(self):
        for trigger_name in self.list_triggers():
            self.drop_trigger(trigger_name)
