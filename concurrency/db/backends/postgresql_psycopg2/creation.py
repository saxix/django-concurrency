from django.db.backends.postgresql_psycopg2.creation import DatabaseCreation
from concurrency.db.backends.utils import get_trigger_name


class PgCreation(DatabaseCreation):
    drop = "DROP TRIGGER {trigger_name}_u ON {opts.db_table};"

    sql = """
ALTER TABLE {opts.db_table} ALTER COLUMN {field.column} SET DEFAULT 1;

CREATE OR REPLACE FUNCTION {trigger_name}_su()
    RETURNS TRIGGER as
    '
    BEGIN
       NEW.{field.column} = OLD.{field.column} +1;
        RETURN NEW;
    END;
    ' language 'plpgsql';

CREATE OR REPLACE FUNCTION {trigger_name}_si()
    RETURNS TRIGGER as
    '
    BEGIN
       NEW.{field.column} = 1;
        RETURN NEW;
    END;
    ' language 'plpgsql';

CREATE TRIGGER {trigger_name}_u BEFORE UPDATE
    ON {opts.db_table} FOR EACH ROW
    EXECUTE PROCEDURE {trigger_name}_su();

CREATE TRIGGER {trigger_name}_i BEFORE INSERT
    ON {opts.db_table} FOR EACH ROW
    EXECUTE PROCEDURE {trigger_name}_si();
"""

    def _create_trigger(self, field):
        from django.db.utils import DatabaseError

        opts = field.model._meta
        trigger_name = get_trigger_name(field, opts)

        stm = self.sql.format(trigger_name=trigger_name,
                              opts=opts,
                              field=field)

        self.connection.drop_trigger('{}_i'.format(trigger_name))
        self.connection.drop_trigger('{}_u'.format(trigger_name))
        try:
            self.connection.cursor().execute(stm)

        except BaseException as exc:
            raise DatabaseError(exc)

        return trigger_name
