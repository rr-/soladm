import asyncio
from soladm import net


def on_connect() -> None:
    print('Connected')


def on_disconnect(reason: str) -> None:
    print('Disconnected ({})'.format(reason))


def on_message(message: str) -> None:
    print('Message received', message)


def on_refresh(game_info: net.GameInfo) -> None:
    print('Refresh')
    print(game_info.map_name)


def run(connection: net.Connection) -> None:
    connection.on_connect.append(on_connect)
    connection.on_disconnect.append(on_disconnect)
    connection.on_message.append(on_message)
    connection.on_refresh.append(on_refresh)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(connection.open())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(connection.close())
    loop.close()
