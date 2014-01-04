from django.db.backends.mysql.base import DatabaseWrapper as MySQLDatabaseWrapper
from concurrency.db.backends.common import TriggerMixin
from concurrency.db.backends.mysql.creation import MySQLCreation


class DatabaseWrapper(TriggerMixin, MySQLDatabaseWrapper):
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.creation = MySQLCreation(self)

    def _clone(self):
        return self.__class__(self.settings_dict, self.alias)

    def list_triggers(self):
        cursor = self.cursor()
        cursor.execute("SHOW TRIGGERS LIKE 'concurrency_%%';")
        return [m[0] for m in cursor.fetchall()]

    def drop_trigger(self, trigger_name):
        cursor = self.cursor()
        result = cursor.execute("DROP TRIGGER IF EXISTS %s;" % trigger_name)
        return result


