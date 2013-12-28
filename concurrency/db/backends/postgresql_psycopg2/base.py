import logging
import re
from django.db.backends.postgresql_psycopg2.base import DatabaseWrapper as PgDatabaseWrapper
from concurrency.db.backends.common import TriggerMixin
from concurrency.db.backends.postgresql_psycopg2.creation import PgCreation

logger = logging.getLogger(__name__)


class DatabaseWrapper(TriggerMixin, PgDatabaseWrapper):
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.creation = PgCreation(self)

    def list_triggers(self):
        cursor = self.cursor()
        stm = "select * from pg_trigger where tgname LIKE 'concurrency_%%'; "
        logger.debug(stm)
        cursor.execute(stm)
        return [m[1] for m in cursor.fetchall()]

    def drop_trigger(self, trigger_name):
        if not trigger_name in self.list_triggers():
            return []
        cursor = self.cursor()
        table_name = re.sub('^concurrency_(.*)_[ui]', '\\1', trigger_name)
        stm = "DROP TRIGGER %s ON %s;" % (trigger_name, table_name)
        logger.debug(stm)
        result = cursor.execute(stm)
        return result
