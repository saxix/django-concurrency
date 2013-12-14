import django.db.utils
import _mysql_exceptions

from django.db.backends.mysql.creation import DatabaseCreation


class MySQLCreation(DatabaseCreation):

    sql = """DELIMITER ||
DROP TRIGGER IF EXISTS %(trigger_name1)s;
||

CREATE TRIGGER %(trigger_name1)s BEFORE INSERT ON %(table)s
BEGIN
FOR EACH ROW BEGIN
    SET NEW.%(col_name)s = UNIX_TIMESTAMP();
END;
||
"""
    def __init__(self, connection):
        super(MySQLCreation, self).__init__(connection)
        self.trigger_fields = []

    def _create_trigger(self, field):
        import MySQLdb as Database
        from warnings import filterwarnings, resetwarnings

        filterwarnings('ignore', message='Trigger does not exist', category=Database.Warning)
        cursor = self.connection.cursor()
        qn = self.connection.ops.quote_name
        db_table = field.model._meta.db_table
        trigger_name = '%s_%s' % (db_table, field.column)

        stm = self.sql % {'trigger_name1': qn('i' + trigger_name),
                          'trigger_name2': qn('u' + trigger_name),
                          'table': qn(db_table),
                          'col_name': field.column}
        try:
            print field, field.model
            cursor.execute(stm)
        except (django.db.utils.ProgrammingError, _mysql_exceptions.ProgrammingError) as e:
            errno, message = e.args
            print 11111111, e
            if errno != 2014:
                raise
        resetwarnings()

