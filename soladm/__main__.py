from getpass import getpass
import argparse
from typing import Optional, Tuple
from pathlib import Path
from soladm import net
from soladm import ui
from soladm.config import config


DEFAULT_PORT = 23073


class HelpFormatter(argparse.HelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)
        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return ', '.join(action.option_strings) + ' ' + args_string


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        'Soldat admin client',
        epilog=(
            'If server credentials are ommitted and are not found in the '
            'config file, you\'ll be asked for them interactively.'),
        formatter_class=HelpFormatter)
    parser.add_argument(
        '-c', '--config', metavar='PATH', help='path to optional config file')
    parser.add_argument(
        '-l', '--log', metavar='PATH', help='path to output logs to')
    parser.add_argument(
        '--host', default=None, help='ip or hostname to connect to')
    parser.add_argument(
        '--port', type=int, default=None,
        help='port to connect on (default: {})'.format(DEFAULT_PORT))
    parser.add_argument(
        '--pass', dest='password', default=None,
        help='server password to connect with')
    return parser.parse_args()


def _load_config(user_path: Optional[str]) -> None:
    config.read(Path(__file__).parent.joinpath('data', 'default_config.ini'))
    if user_path:
        config.read(Path(user_path))


def _get_connection_info(args: argparse.Namespace) -> Tuple[str, int, str]:
    host: Optional[str] = None
    host = args.host or config.connection.host
    while not host:
        host = input('Enter host: ')

    port: int = args.port or config.connection.port or DEFAULT_PORT

    password: Optional[str] = args.password or config.connection.password
    while not password:
        password = getpass('Enter password: ')

    assert host
    assert port
    assert password
    return (host, port, password)


def main() -> None:
    args = parse_args()
    _load_config(args.config)

    log_path = args.log or config.log.path
    host, port, password = _get_connection_info(args)

    connection = net.Connection(host, port, password)
    ui.run(connection, Path(log_path) if log_path else None)


if __name__ == '__main__':
    main()
