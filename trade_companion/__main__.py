""" Main entrypoint """

from trade_companion.cmd import COMMAND_PARSER
from trade_companion.cmd import *  # pylint: disable=wildcard-import,unused-wildcard-import # noqa


def main():
    """ Parse arguments and execute sub-command """
    args = COMMAND_PARSER.parse_args()

    # import cProfile
    # cProfile.run('args.func(args)', options.profile_output)

    args.func(args)


if __name__ == "__main__":
    main()
