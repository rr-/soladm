import asyncio
import io
import struct
from enum import IntEnum


def _read_u8(stream) -> int:
    return struct.unpack('<B', stream.read(1))[0]

def _read_u16_le(stream) -> int:
    return struct.unpack('<H', stream.read(2))[0]

def _read_u32_le(stream) -> int:
    return struct.unpack('<i', stream.read(4))[0]

def _read_bytes(stream, size: int) -> bytes:
    return stream.read(size)

def _read_var_str(stream, size: int) -> str:
    len = _read_u8(stream)
    assert len < size
    return stream.read(size)[0:len].decode('latin1')


class PlayerTeam(IntEnum):
    NONE = 0
    ALPHA = 1
    BRAVO = 2
    CHARLIE = 3
    DELTA = 4
    SPECTATOR = 5
    UNASSIGNED = 255


class GameMode(IntEnum):
    DeathMatch = 0
    PointMatch = 1
    TeamMatch = 2
    CaptureTheFlag = 3
    RamboMatch = 4
    Infiltration = 5
    HoldTheFlag = 6


class PlayerInfo:
    def __init__(self) -> None:
        self.id = 0
        self.name = ''
        self.team = PlayerTeam.NONE
        self.kills = 0
        self.caps = 0
        self.deaths = 0
        self.ping = 0
        self.ip = '0.0.0.0'


class GameInfo:
    def __init__(self) -> None:
        self.scores = {
            PlayerTeam.ALPHA: 0,
            PlayerTeam.BRAVO: 0,
            PlayerTeam.CHARLIE: 0,
            PlayerTeam.DELTA: 0,
        }
        self.map_name = ''
        self.game_mode = GameMode.DeathMatch
        self.current_time = 0
        self.time_limit = 0
        self.score_limit = 0
        self._players: List[PlayerInfo] = [PlayerInfo() for i in range(32)]

    @property
    def players(self):
        return [
            player
            for player in self._players
            if player.team != UNASSIGNED]

    def update_from_refresh_packet(self, data: bytes) -> None:
        stream = io.BytesIO(data)
        for i in range(32):
            self._players[i].name = _read_var_str(stream, 24)
        for i in range(32):
            self._players[i].team = PlayerTeam(_read_u8(stream))
        for i in range(32):
            self._players[i].kills = _read_u16_le(stream)
        for i in range(32):
            self._players[i].deaths = _read_u16_le(stream)
        for i in range(32):
            self._players[i].ping = _read_u8(stream)
        for i in range(32):
            self._players[i].id = _read_u8(stream)
        for i in range(32):
            self._players[i].ip = '.'.join(
                str(octet) for octet in [_read_u8(stream) for i in range(4)])
        for team in (
                PlayerTeam.ALPHA,
                PlayerTeam.BRAVO,
                PlayerTeam.CHARLIE,
                PlayerTeam.DELTA):
            self.scores[team] = _read_u16_le(stream)
        self.map_name = _read_var_str(stream, 16)
        self.time_limit = _read_u32_le(stream)
        self.current_time = _read_u32_le(stream)
        self.score_limit = _read_u16_le(stream)
        self.game_mode = GameMode(_read_u8(stream))


class State:
    def __init__(self):
        self.game_info = GameInfo()

    def on_connect(self) -> None:
        print('Connected')

    def on_disconnect(self) -> None:
        print('Disconnected')

    def on_message(self, message: str) -> None:
        print('Message received', message)

    def on_refresh(self) -> None:
        print('Refresh')
        print(self.game_info.map_name)

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
                        state.game_info.update_from_refresh_packet(data)
                        state.on_refresh()
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
