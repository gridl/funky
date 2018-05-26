"""Initialize and run localalias."""

import argparse
import enum
import sys

import localalias
from localalias import commands
from localalias.utils import log

_LALIAS_METAVAR = 'LocalAliasName'


def main(argv=None):
    try:
        log.logger.debug('Starting localalias.')

        if argv is None:
            argv = sys.argv[1:]

        parser = _get_argparser()
        args = parser.parse_args(argv)
        log.init_logger(debug=args.debug)
        _validate_args(args)
        cmd, pargs, kwargs = _Actions.cmd_map(args)
        cmd(*pargs, **kwargs)
    except ValueError as e:
        log.logger.error('%s\n', str(e))
        parser.print_usage()
    except RuntimeError as e:
        log.logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        log.logger.exception('{}: {}'.format(type(e).__name__, str(e)))
        raise


def _get_argparser():
    """Get command-line arguments.

    Returns:
        argparse.ArgumentParser object.
    """
    parser = argparse.ArgumentParser(prog='localalias', description=localalias.__doc__)
    parser.add_argument('lalias', nargs='?', default=None, metavar=_LALIAS_METAVAR,
            help='Name of the local alias/function.')
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug mode.")
    action = parser.add_mutually_exclusive_group()
    action.add_argument('-a', _Actions.opt_map(_Actions.ADD), dest='action', action='store_const',
            const=_Actions.ADD,
            help='Add a new local alias/function.')
    action.add_argument('-r', _Actions.opt_map(_Actions.REMOVE), dest='action', action='store_const',
            const=_Actions.REMOVE,
            help='Remove an existing local alias/function.')
    action.add_argument('-e', _Actions.opt_map(_Actions.EDIT), dest='action', action='store_const',
            const=_Actions.EDIT,
            help='Edit local .lshrc file manually.')
    action.add_argument('-s', _Actions.opt_map(_Actions.SHOW), dest='action', action='store_const',
            const=_Actions.SHOW,
            help='Show an existing local alias/function. If this command is given without an '
            'argument, all local aliases/functions in scope (with respect to the current '
            'directory) are displayed.')
    action.add_argument('-x', _Actions.opt_map(_Actions.EXECUTE), dest='action', action='store_const',
            const=_Actions.EXECUTE, help='Execute an existing local alias/function.')
    action.set_defaults(action=_Actions.EXECUTE)

    return parser


class _Actions(enum.Enum):
    """Action Flags"""
    ADD = enum.auto()
    REMOVE = enum.auto()
    EDIT = enum.auto()
    EXECUTE = enum.auto()
    SHOW = enum.auto()

    @classmethod
    def opt_map(cls, action):
        return {cls.ADD: '--add',
                cls.REMOVE: '--remove',
                cls.EDIT: '--edit',
                cls.EXECUTE: '--execute',
                cls.SHOW: '--show'}[action]

    @classmethod
    def cmd_map(cls, action, args):
        """Given @action, returns corresponding command function and parameters.

        This function aims to insulate the rest of this module from the command API.

        Returns:
            3-Tuple consisting of (<callable command>, <positional args>, <keyword args>).
        """
        cmd = {cls.ADD: commands.add,
               cls.REMOVE: commands.remove,
               cls.EDIT: commands.edit,
               cls.EXECUTE: commands.execute,
               cls.SHOW: commands.show}[action]

        pargs = [args.action, args.lalias]

        kwargs = {}
        if action == cls.SHOW:
            kwargs['color'] = args.color

        return cmd, pargs, kwargs


def _validate_args(args):
    """Validates command-line arguments.

    Returns:
        @args unchanged (argparse.Namespace object), if all validation checks pass. Otherwise,
        a ValueError exception is thrown.
    """
    try:
        if args.action in [_Actions.ADD, _Actions.REMOVE, _Actions.EXECUTE]:
            assert args.lalias is not None
        return args
    except AssertionError as e:
        msg = 'Must also provide {} when using the {} option.'
        raise ValueError(msg.format(_LALIAS_METAVAR, _Actions.opt_map(args.action)))
