# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import sys
from django.db import router, connections


def get_trigger_name(field):
    """

    :param field: Field instance
    :param opts: Options (Model._meta)
    :return:
    """
    opts = field.model._meta
    return 'concurrency_{1.db_table}_{0.name}'.format(field, opts)


def get_triggers(*databases):
    if databases is None:
        databases = [alias for alias in connections]

    triggers = {}
    for alias in databases:
        connection = connections[alias]
        if hasattr(connection, 'list_triggers'):
            triggers[alias] = [trigger_name for trigger_name in connection.list_triggers()]
    return triggers


def drop_triggers(*databases):
    if databases is None:
        databases = [alias for alias in connections]
    triggers = {}
    for alias in databases:
        connection = connections[alias]
        if hasattr(connection, 'drop_triggers'):
            connection.drop_triggers()

    return triggers


def create_triggers(databases, stdout=None):
    global _TRIGGERS
    from concurrency.fields import _TRIGGERS
    for field in set(_TRIGGERS):
        model = field.model
        alias = router.db_for_write(model)
        if alias in databases:
            if stdout:
                stdout.write(alias)
            if not field._trigger_exists:
                connection = connections[alias]
                f = factory(connection)
                f.create(field)
    _TRIGGERS = []


class TriggerFactory(object):
    insert_clause = ""
    update_clause = ""
    drop_clause = ""
    list_clause = ""

    def __init__(self, connection):
        self.connection = connection

    def create(self, field):
        from django.db.utils import DatabaseError

        opts = field.model._meta
        triggers = self.list()
        for sfx, clause in [('_i', self.insert_clause), ('_u', self.update_clause)]:
            trigger_name = "{}_{}".format(field.trigger_name, sfx)
            if trigger_name not in triggers:
                stm = clause.format(trigger_name=trigger_name,
                                    opts=opts,
                                    field=field)
                try:
                    self.connection.cursor().execute(stm)
                except BaseException as exc:  # pragma: no cover
                    raise DatabaseError("""Error executing:
{1}
{0}""".format(exc, stm))
        field._trigger_exists = True

    def drop(self, field):
        opts = field.model._meta
        for sfx in ['_i', '_u']:
            trigger_name = "{}_{}".format(field.trigger_name, sfx)
            stm = self.drop_clause.format(trigger_name=trigger_name,
                                          opts=opts,
                                          field=field)
            self.connection.cursor().execute(stm)

    def _list(self):
        cursor = self.connection.cursor()
        cursor.execute(self.list_clause)
        return cursor.fetchall()

    def list(self):
        return sorted([m[0] for m in self._list()])


class Sqlite3(TriggerFactory):
    drop_clause = """DROP TRIGGER IF EXISTS {trigger_name};"""

    update_clause = """
CREATE TRIGGER {trigger_name}
AFTER UPDATE ON {opts.db_table}
BEGIN UPDATE {opts.db_table} SET {field.column} = {field.column}+1 WHERE {opts.pk.column} = NEW.{opts.pk.column};
END;"""
    insert_clause = """
CREATE TRIGGER {trigger_name}
AFTER INSERT ON {opts.db_table}
BEGIN UPDATE {opts.db_table} SET {field.column} = 0 WHERE {opts.pk.column} = NEW.{opts.pk.column};
END;
"""
    list_clause = "select name from sqlite_master where type='trigger';"

    # def list_triggers(self, connectio):
    #     cursor = self.cursor()
    #     result = cursor.execute("select name from sqlite_master where type='trigger';")
    #     return sorted([m[0] for m in result.fetchall()])


class PostgreSQL(TriggerFactory):
    drop_clause = r"""DROP TRIGGER IF EXISTS {trigger_name} ON {opts.db_table};"""

    update_clause = r"""

CREATE OR REPLACE FUNCTION func_{trigger_name}()
    RETURNS TRIGGER as
    '
    BEGIN
       NEW.{field.column} = OLD.{field.column} +1;
        RETURN NEW;
    END;
    ' language 'plpgsql';

CREATE TRIGGER {trigger_name} BEFORE UPDATE
    ON {opts.db_table} FOR EACH ROW
    EXECUTE PROCEDURE func_{trigger_name}();
    """

    insert_clause = r"""ALTER TABLE {opts.db_table} ALTER COLUMN {field.column} SET DEFAULT 1;

CREATE OR REPLACE FUNCTION func_{trigger_name}()
    RETURNS TRIGGER as
    '
    BEGIN
       NEW.{field.column} = 1;
        RETURN NEW;
    END;
    ' language 'plpgsql';

CREATE TRIGGER {trigger_name} BEFORE INSERT
    ON {opts.db_table} FOR EACH ROW
    EXECUTE PROCEDURE func_{trigger_name}();
"""
    list_clause = "select * from pg_trigger where tgname LIKE 'concurrency_%%'; "

    def list(self):
        return sorted([m[1] for m in self._list()])


class MySQL(TriggerFactory):
    drop_clause = """DROP TRIGGER IF EXISTS {trigger_name};"""

    insert_clause = """
ALTER TABLE {opts.db_table} CHANGE `{field.column}` `{field.column}` BIGINT(20) NOT NULL DEFAULT 1;

CREATE TRIGGER {trigger_name} BEFORE INSERT ON {opts.db_table}
FOR EACH ROW SET NEW.{field.column} = 1 ;

"""

    update_clause = """
CREATE TRIGGER {trigger_name} BEFORE UPDATE ON {opts.db_table}
FOR EACH ROW SET NEW.{field.column} = OLD.{field.column}+1;
"""

    list_clause = "SHOW TRIGGERS"

    # def _create_trigger(self, field):
    #     # import MySQLdb as Database
    #     from warnings import filterwarnings, resetwarnings
    #     import _mysql_exceptions
    #
    #     filterwarnings('ignore', message='Trigger does not exist',
    #                    category=Warning)
    #
    #     opts = field.model._meta
    #     trigger_name = get_trigger_name(field, opts)
    #
    #     stm = self.sql.format(trigger_name=trigger_name,
    #                           opts=opts, field=field)
    #     cursor = self.connection._clone().cursor()
    #     try:
    #         cursor.execute(stm)
    #         self._triggers[field] = trigger_name
    #
    #     except (BaseException, _mysql_exceptions.ProgrammingError) as exc:
    #         errno, message = exc.args
    #         if errno != 2014:
    #             import traceback
    #             traceback.print_exc(exc)
    #             raise
    #     resetwarnings()
    #     return trigger_name


def factory(conn):
    try:
        return {'postgresql': PostgreSQL,
                'mysql': MySQL,
                'sqlite3': Sqlite3,
                'sqlite': Sqlite3,
                }[conn.vendor](conn)
    except KeyError:
        raise ValueError('{} is not supported by TriggerVersionField'.format(conn))
