from getpass import getpass
import asyncio
import configargparse
from soladm import net


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

    loop = asyncio.get_event_loop()
    connection = loop.run_until_complete(net.connect(host, port, password))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(connection.close())
    loop.close()


if __name__ == '__main__':
    main()
