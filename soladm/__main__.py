from getpass import getpass
import argparse
from typing import Optional, Tuple
from pathlib import Path
from soladm import config
from soladm import net
from soladm import ui


DEFAULT_PORT = 23073


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Soldat admin client')
    parser.add_argument('-c', '--config', help='path to optional config file')
    parser.add_argument(
        '--host', help='ip or hostname to connect to')
    parser.add_argument(
        '--port', type=int, help='default: {}'.format(DEFAULT_PORT))
    parser.add_argument(
        '--pass', dest='password', default='',
        help='if ommitted, you\'ll be asked for it interactively')
    return parser.parse_args()


def _load_config(user_path: Optional[str]) -> None:
    config.read_config(
        Path(__file__).parent.joinpath('data', 'default_config.ini'))
    if user_path:
        config.read_config(Path(user_path))


def _get_connection_info(args: argparse.Namespace) -> Tuple[str, int, str]:
    cfg = config.get_config()

    host: Optional[str] = None
    host = args.host or cfg.connection.host
    while not host:
        host = input('Enter host: ')

    port: int = args.port or cfg.connection.port or DEFAULT_PORT

    password: Optional[str] = args.password or cfg.connection.password
    while not password:
        password = getpass('Enter password: ')

    assert host
    assert port
    assert password
    return (host, port, password)


def main() -> None:
    args = parse_args()
    _load_config(args.config)
    host, port, password = _get_connection_info(args)
    connection = net.Connection(host, port, password)
    ui.run(connection)


if __name__ == '__main__':
    main()
