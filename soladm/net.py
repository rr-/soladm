import asyncio


class State:
    def on_connect(self) -> None:
        print('Connected')

    def on_disconnect(self) -> None:
        print('Disconnected')

    def on_message(self, message: str) -> None:
        print('Message received', message)

    def on_refresh(self, message: bytes) -> None:
        print('Refresh', message)

    def on_refreshx(self, message: bytes) -> None:
        print('Refresh x', message)


async def connect(loop, host: str, port: int, password: str):
    state = State()

    async def connect():
        try:
            reader, writer = await asyncio.open_connection(
                host, port, loop=loop)

            writer.write('{}\r\n'.format(password).encode())
            await writer.drain()

            state.on_connect()
        except ConnectionResetError as ex:
            state.on_disconnect()
            await asyncio.sleep(1)
            await connect()

        writer.write('REFRESH\r\n'.encode())
        await writer.drain()

        async def read():
            while True:
                try:
                    line = (
                        (await reader.readline())
                        .decode('latin-1')
                        .rstrip('\r\n'))
                    if line == 'REFRESH':
                        data = await reader.read(1188)
                        state.on_refresh(data)
                    elif line == 'REFRESHX':
                        data = await reader.read(1992)
                        state.on_refreshx(data)
                    else:
                        state.on_message(line)
                except ConnectionResetError as ex:
                    state.on_disconnect()
                    await asyncio.sleep(1)
                    await connect()
                    return
                except Exception as ex:
                    print(ex)
                    await asyncio.sleep(1)
                    await connect()
                    return

        asyncio.ensure_future(read(), loop=loop)

    await connect()
