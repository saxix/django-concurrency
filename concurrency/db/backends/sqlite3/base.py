# from django.db.backends.sqlite3.base import *
from django.db.backends.sqlite3.base import DatabaseWrapper as Sqlite3DatabaseWrapper
from concurrency.db.backends.common import TriggerMixin
from concurrency.db.backends.sqlite3.creation import Sqlite3Creation


class DatabaseWrapper(TriggerMixin, Sqlite3DatabaseWrapper):
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.creation = Sqlite3Creation(self)

    def list_triggers(self):
        cursor = self.cursor()
        result = cursor.execute("select name from sqlite_master where type = 'trigger';")
        return [m[0] for m in result.fetchall()]

    def drop_trigger(self, trigger_name):
        cursor = self.cursor()
        result = cursor.execute("DROP TRIGGER IF EXISTS %s;" % trigger_name)
        return result
