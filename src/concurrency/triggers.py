# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from collections import defaultdict

from django.db import connections, router
from django.db.utils import DatabaseError

from concurrency.fields import _TRIGGERS  # noqa


def get_trigger_name(field):
    """

    :param field: Field instance
    :return: unicode
    """
    if field._trigger_name:
        name = field._trigger_name
    else:
        name = '{1.db_table}_{0.name}'.format(field, field.model._meta)
    return 'concurrency_{}'.format(name)


def get_triggers(databases=None):
    if databases is None:
        databases = [alias for alias in connections]

    ret = {}
    for alias in databases:
        connection = connections[alias]
        f = factory(connection)
        r = f.get_list()
        ret[alias] = r
    return ret


def drop_triggers(*databases):
    global _TRIGGERS
    ret = defaultdict(lambda: [])
    for field in set(_TRIGGERS):
        model = field.model
        alias = router.db_for_write(model)
        if alias in databases:
            connection = connections[alias]
            f = factory(connection)
            f.drop(field)
            field._trigger_exists = False
            ret[alias].append([model, field, field.trigger_name])
    return ret


def create_triggers(databases):
    global _TRIGGERS
    ret = defaultdict(lambda: [])

    for field in set(_TRIGGERS):
        model = field.model
        alias = router.db_for_write(model)
        if alias in databases:
            if not field._trigger_exists:
                field._trigger_exists = True
                connection = connections[alias]
                f = factory(connection)
                f.create(field)
                ret[alias].append([model, field, field.trigger_name])
    # _TRIGGERS = []
    return ret


class TriggerFactory(object):
    update_clause = ""
    drop_clause = ""
    list_clause = ""

    def __init__(self, connection):
        self.connection = connection

    def get_trigger(self, field):
        if field.trigger_name in self.get_list():
            return field.trigger_name
        return None

    def create(self, field):
        if field.trigger_name not in self.get_list():
            stm = self.update_clause.format(trigger_name=field.trigger_name,
                                            opts=field.model._meta,
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
        ret = []
        stm = self.drop_clause.format(trigger_name=field.trigger_name,
                                      opts=opts,
                                      field=field)
        self.connection.cursor().execute(stm)
        ret.append(field.trigger_name)
        return ret

    def _list(self):
        cursor = self.connection.cursor()
        cursor.execute(self.list_clause)
        return cursor.fetchall()

    def get_list(self):
        return sorted([m[0] for m in self._list()])


class Sqlite3(TriggerFactory):
    drop_clause = """DROP TRIGGER IF EXISTS {trigger_name};"""

    update_clause = """CREATE TRIGGER {trigger_name}
AFTER UPDATE ON {opts.db_table}
BEGIN UPDATE {opts.db_table} SET {field.column} = {field.column}+1 WHERE {opts.pk.column} = NEW.{opts.pk.column};
END;"""

    list_clause = "select name from sqlite_master where type='trigger';"


class PostgreSQL(TriggerFactory):
    drop_clause = r"""DROP TRIGGER IF EXISTS {trigger_name} ON {opts.db_table};"""

    update_clause = r"""CREATE OR REPLACE FUNCTION func_{trigger_name}()
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

    list_clause = "select * from pg_trigger where tgname LIKE 'concurrency_%%'; "

    def get_list(self):
        return sorted([m[1] for m in self._list()])


class MySQL(TriggerFactory):
    drop_clause = """DROP TRIGGER IF EXISTS {trigger_name};"""

    update_clause = """
CREATE TRIGGER {trigger_name} BEFORE UPDATE ON {opts.db_table}
FOR EACH ROW SET NEW.{field.column} = OLD.{field.column}+1;
"""

    list_clause = "SHOW TRIGGERS"


def factory(conn):
    try:
        return {'postgresql': PostgreSQL,
                'mysql': MySQL,
                'sqlite3': Sqlite3,
                'sqlite': Sqlite3,
                }[conn.vendor](conn)
    except KeyError:
        raise ValueError('{} is not supported by TriggerVersionField'.format(conn))
