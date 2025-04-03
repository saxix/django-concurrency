from functools import partial

import django
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.transaction import atomic

from concurrency.triggers import create_triggers, drop_triggers, get_triggers


def _add_subparser(subparsers, parser, name, help) -> None:
    if django.VERSION >= (2, 1):
        subparsers.add_parser(name, help=help)
    else:
        subparsers.add_parser(name, cmd=parser, help=help)


class Command(BaseCommand):
    args = ""
    help = "register Report classes and create one ReportConfiguration per each"

    requires_system_checks = []

    def add_arguments(self, parser) -> None:
        """
        Entry point for subclassed commands to add custom arguments.
        """
        subparsers = parser.add_subparsers(help="sub-command help", dest="command")

        add_parser = partial(_add_subparser, subparsers, parser)

        add_parser("list", help="list concurrency triggers")
        add_parser("drop", help="drop  concurrency triggers")
        add_parser("create", help="create concurrency triggers")

        parser.add_argument(
            "-d",
            "--database",
            action="store",
            dest="database",
            default=None,
            help="limit to this database",
        )

        parser.add_argument(
            "-t",
            "--trigger",
            action="store",
            dest="trigger",
            default=None,
            help="limit to this trigger name",
        )

    def _list(self, databases) -> None:
        for alias, triggers in get_triggers(databases).items():
            self.stdout.write(f"Database: {alias}")
            for trigger in triggers:
                self.stdout.write(f"       {trigger}")
        self.stdout.write("")

    def handle(self, *args, **options) -> None:
        cmd = options["command"]
        database = options["database"]
        databases = list(connections) if database is None else [database]

        with atomic():
            try:
                if cmd == "list":
                    self._list(databases)
                elif cmd == "create":
                    for alias, triggers in create_triggers(databases).items():
                        self.stdout.write(f"Database: {alias}")
                        for trigger in triggers:
                            self.stdout.write(f"    Created {trigger[2]}  for {trigger[1]}")
                    self.stdout.write("")
                elif cmd == "drop":
                    for alias, triggers in drop_triggers(*databases).items():
                        self.stdout.write(f"Database: {alias}")
                        for trigger in triggers:
                            self.stdout.write(f"    Dropped   {trigger[2]}")
                    self.stdout.write("")
                else:  # pragma: no cover
                    raise Exception
            except ImproperlyConfigured as e:  # pragma: no cover
                self.stdout.write(self.style.ERROR(e))
