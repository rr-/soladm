from getpass import getpass
import configargparse
from soladm import net, ui


def parse_args() -> configargparse.Namespace:
    parser = configargparse.ArgumentParser('Soldat admin client')
    parser.add_argument('host')
    parser.add_argument('port', type=int)
    parser.add_argument('password', default='', nargs='?')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    host: str = args.host
    port: int = args.port
    password: str = args.password or getpass('Enter password: ')

    connection = net.Connection(host, port, password)
    ui.run(connection)


if __name__ == '__main__':
    main()
