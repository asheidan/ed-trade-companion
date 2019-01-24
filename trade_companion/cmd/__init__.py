""" Root command information

This module also auto exposes all other modules in the same directory
which makes it possible to import all commands.
"""

import argparse
import logging
import os

__all__ = sorted(d[:-3]
                 for d in os.listdir(os.path.dirname(__file__))
                 if (d.endswith('.py') and d[0] not in '._'
                     and not d.startswith("flycheck_")))
# print(__all__)

COMMAND_PARSER = argparse.ArgumentParser(
    prog="ed-trade-companion",
    )

_LOG_LEVEL_STRINGS = ['critical', 'error', 'warning', 'info', 'debug']
def _log_level_from_string(log_level_name):
    if log_level_name in _LOG_LEVEL_STRINGS:
        return getattr(logging, log_level_name.upper())
    else:
        raise Exception("Unknown log-level: %s" % log_level_name)


COMMAND_PARSER.add_argument(
    "--log-level", action="store",
    type=_log_level_from_string, default=logging.INFO)

SUB_COMMAND_PARSER = COMMAND_PARSER.add_subparsers(
    title="sub-commands", metavar="COMMAND")
