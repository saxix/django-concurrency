from django.db.backends.mysql.base import *
from django.db.backends.mysql.base import DatabaseWrapper as MySQLDatabaseWrapper
from concurrency.db.backends.mysql.creation import MySQLCreation


class DatabaseWrapper(MySQLDatabaseWrapper):
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.creation = MySQLCreation(self)
