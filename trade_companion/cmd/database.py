""" Functionality related to the import command """

from trade_companion.cmd import SUB_COMMAND_PARSER

DATABASE_PARSER = SUB_COMMAND_PARSER.add_parser(
    'database', aliases=['db'],
    help="Database related functionality.")
SUB_DATABASE_PARSER = DATABASE_PARSER.add_subparsers(
    title="sub-commands", metavar="SUBCOMMAND")
