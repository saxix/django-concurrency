import _mysql_exceptions

from django.db.backends.mysql.creation import DatabaseCreation
from concurrency.db.backends.utils import get_trigger_name


class MySQLCreation(DatabaseCreation):
    sql = """
ALTER TABLE {opts.db_table} CHANGE `{field.column}` `{field.column}` BIGINT(20) NOT NULL DEFAULT 1;
DROP TRIGGER IF EXISTS {trigger_name}_i;
DROP TRIGGER IF EXISTS {trigger_name}_u;

CREATE TRIGGER {trigger_name}_i BEFORE INSERT ON {opts.db_table}
FOR EACH ROW SET NEW.{field.column} = 1 ;
CREATE TRIGGER {trigger_name}_u BEFORE UPDATE ON {opts.db_table}
FOR EACH ROW SET NEW.{field.column} = OLD.{field.column}+1;
"""


    def _create_trigger(self, field):
        import MySQLdb as Database
        from warnings import filterwarnings, resetwarnings

        filterwarnings('ignore', message='Trigger does not exist', category=Database.Warning)

        opts = field.model._meta
        trigger_name = get_trigger_name(field, opts)

        stm = self.sql.format(trigger_name=trigger_name, opts=opts, field=field)
        cursor = self.connection._clone().cursor()
        try:
            cursor.execute(stm)
        except (BaseException, _mysql_exceptions.ProgrammingError) as exc:
            errno, message = exc.args
            if errno != 2014:
                import traceback
                traceback.print_exc(exc)
                raise
        resetwarnings()
        return trigger_name
