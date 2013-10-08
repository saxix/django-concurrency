
from django.db.backends.mysql.creation import DatabaseCreation


class MySQLCreation(DatabaseCreation):


    sql = """DROP TRIGGER IF EXISTS %(trigger_name)s;
CREATE TRIGGER %(trigger_name)s BEFORE INSERT ON %(table)s
FOR EACH ROW BEGIN
    SET NEW.%(col_name)s = UNIX_TIMESTAMP();
END;

"""


    def sql_indexes_for_field(self, model, f, style):
        output = super(MySQLCreation, self).sql_indexes_for_field(model, f, style)
        from concurrency.fields import TriggerVersionField
        if isinstance(f, TriggerVersionField):
            qn = self.connection.ops.quote_name
            db_table = model._meta.db_table
            trigger_name = '%s_%s_trigger' % (db_table, f.column)
            output.append(self.sql % {'trigger_name': qn(trigger_name),
                                      'table' : style.SQL_TABLE(qn(db_table)),

                                      })
            # output.append(style.SQL_KEYWORD('CREATE SPATIAL INDEX ') +
            #               style.SQL_TABLE(qn(idx_name)) +
            #               style.SQL_KEYWORD(' ON ') +
            #               style.SQL_TABLE(qn(db_table)) + '(' +
            #               style.SQL_FIELD(qn(f.column)) + ');')
        return output
