""" Functionality related to the database migrate sub-command  """

import argparse

from trade_companion.cmd.database import SUB_DATABASE_PARSER
from trade_companion import models

MIGRATE_DATABASE_PARSER = SUB_DATABASE_PARSER.add_parser(
    "migrate", aliases=["mig"],
    help="Automigrate the database.")


def main(_options: argparse.Namespace) -> None:
    # pylint: disable=missing-docstring
    print("Migrating databases")
    models.create_tables()


MIGRATE_DATABASE_PARSER.set_defaults(func=main)
