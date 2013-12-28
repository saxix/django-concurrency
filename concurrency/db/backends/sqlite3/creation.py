from django.db.backends.sqlite3.creation import DatabaseCreation
from concurrency.db.backends.utils import get_trigger_name


class Sqlite3Creation(DatabaseCreation):
    sql = """
DROP TRIGGER IF EXISTS {trigger_name}_u; ##

CREATE TRIGGER {trigger_name}_u
AFTER UPDATE ON {opts.db_table}
BEGIN UPDATE {opts.db_table} SET {field.column} = {field.column}+1 WHERE {opts.pk.column} = NEW.{opts.pk.column};
END; ##

DROP TRIGGER IF EXISTS {trigger_name}_i; ##

CREATE TRIGGER {trigger_name}_i
AFTER INSERT ON {opts.db_table}
BEGIN UPDATE {opts.db_table} SET {field.column} = 0 WHERE {opts.pk.column} = NEW.{opts.pk.column};
END; ##
"""

    def _create_trigger(self, field):
        from django.db.utils import DatabaseError
        cursor = self.connection.cursor()

        opts = field.model._meta
        trigger_name = get_trigger_name(field, opts)

        stms = self.sql.split('##')
        for template in stms:
            stm = template.format(trigger_name=trigger_name,
                                  opts=opts,
                                  field=field)
            try:
                cursor.execute(stm)
            except BaseException as exc:
                raise DatabaseError(exc)

        return trigger_name
