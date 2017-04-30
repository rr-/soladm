from getpass import getpass
import argparse
from pathlib import Path
from soladm import config
from soladm import net
from soladm import ui


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Soldat admin client')
    parser.add_argument('host')
    parser.add_argument('port', type=int)
    parser.add_argument('password', default='', nargs='?')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    host: str = args.host
    port: int = args.port
    password: str = args.password or getpass('Enter password: ')

    config.read_config(
        Path(__file__).parent.joinpath('data', 'default_config.ini'))

    connection = net.Connection(host, port, password)
    ui.run(connection)


if __name__ == '__main__':
    main()
