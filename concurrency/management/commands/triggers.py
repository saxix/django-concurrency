# -*- coding: utf-8 -*-
from optparse import make_option
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from django.db import connections
from concurrency.db.compat import atomic
from concurrency.utils import create_triggers, get_triggers, drop_triggers


class Command(BaseCommand):
    args = ''
    help = 'register Report classes and create one ReportConfiguration per each'
    option_list = BaseCommand.option_list + (
        make_option('-d', '--database',
                    action='store',
                    dest='database',
                    default=None,
                    help='limit to this database'),
        make_option('-t', '--trigger',
                    action='store',
                    dest='trigger',
                    default=None,
                    help='limit to this trigger name'))

    def _list(self, databases):
        FMT = "{:20} {}\n"
        self.stdout.write(FMT.format('DATABASE', 'TRIGGERS'))
        for alias, triggers in get_triggers(databases).items():
            self.stdout.write(FMT.format(alias, ", ".join(triggers)))
        self.stdout.write('')

    def handle(self, cmd='list', *args, **options):
        database = options['database']
        if database is None:
            databases = [alias for alias in connections]
        else:
            databases = [database]

        with atomic():
            try:
                if cmd == 'list':
                    self._list(databases)
                elif cmd == 'create':
                    create_triggers(databases)
                    self._list(databases)
                elif cmd == 'drop':
                    drop_triggers(databases)
                    self._list(databases)
                else:
                    raise Exception()
            except ImproperlyConfigured as e:
                self.stdout.write(self.style.ERROR(e))
