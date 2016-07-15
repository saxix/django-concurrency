# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from django.db import connections

from concurrency.compat import atomic
from concurrency.triggers import create_triggers, drop_triggers, get_triggers


class Command(BaseCommand):
    args = ''
    help = 'register Report classes and create one ReportConfiguration per each'

    requires_system_checks = False

    def add_arguments(self, parser):
        """
        Entry point for subclassed commands to add custom arguments.
        """
        subparsers = parser.add_subparsers(help='sub-command help',
                                           dest='command')

        subparsers.add_parser('list',
                              cmd=parser,
                              help="command_a help")
        subparsers.add_parser('drop',
                              cmd=parser,
                              help="command_a help")
        subparsers.add_parser('create',
                              cmd=parser,
                              help="command_a help")

        parser.add_argument('-d', '--database',
                            action='store',
                            dest='database',
                            default=None,
                            help='limit to this database')

        parser.add_argument('-t', '--trigger',
                            action='store',
                            dest='trigger',
                            default=None,
                            help='limit to this trigger name')

    def _list(self, databases):
        for alias, triggers in get_triggers(databases).items():
            self.stdout.write("Database: {}".format(alias))
            for trigger in triggers:
                self.stdout.write("       {}".format(trigger))
        self.stdout.write('')

    def handle(self, *args, **options):

        cmd = options['command']
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
                    for alias, triggers in create_triggers(databases).items():
                        self.stdout.write("Database: {}".format(alias))
                        for trigger in triggers:
                            self.stdout.write("    Created {0[2]}  for {0[1]}".format(trigger))
                    self.stdout.write('')
                elif cmd == 'drop':
                    for alias, triggers in drop_triggers(*databases).items():
                        self.stdout.write("Database: {}".format(alias))
                        for trigger in triggers:
                            self.stdout.write("    Dropped   {0[2]}".format(trigger))
                    self.stdout.write('')
                else:
                    raise Exception()
            except ImproperlyConfigured as e:
                self.stdout.write(self.style.ERROR(e))
