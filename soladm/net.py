import asyncio
import io
import struct
from typing import Optional, List, Callable, Awaitable
from enum import IntEnum


POLL_INTERVAL = 0.5


def _read_u8(stream: io.BytesIO) -> int:
    return struct.unpack('<B', stream.read(1))[0]


def _read_u16_le(stream: io.BytesIO) -> int:
    return struct.unpack('<H', stream.read(2))[0]


def _read_u32_le(stream: io.BytesIO) -> int:
    return struct.unpack('<i', stream.read(4))[0]


def _read_f32(stream: io.BytesIO) -> int:
    return struct.unpack('<f', stream.read(4))[0]


def _read_bytes(stream: io.BytesIO, size: int) -> bytes:
    return stream.read(size)


def _read_var_str(stream: io.BytesIO, size: int) -> str:
    length = _read_u8(stream)
    assert length < size
    return stream.read(size)[0:length].decode('latin1')


class Point:
    def __init__(self) -> None:
        self.x = 0
        self.y = 0


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
        self.hwid = b''
        self.name = ''
        self.team = PlayerTeam.NONE
        self.kills = 0
        self.caps = 0
        self.caps = 0
        self.deaths = 0
        self.ping = 0
        self.ip = '0.0.0.0'
        self.pos = Point()


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
        self.time_left = 0
        self.time_limit = 0
        self.score_limit = 0
        self._players = [PlayerInfo() for i in range(32)]
        self.red_flag_pos = Point()
        self.blue_flag_pos = Point()
        self.max_players = 0
        self.max_spectators = 0
        self.game_passworded = False
        self.next_map_name = ''

    @property
    def players(self) -> List[PlayerInfo]:
        return [
            player
            for player in self._players
            if player.team != PlayerTeam.UNASSIGNED]

    def update_from_refreshx_packet(self, data: bytes) -> None:
        stream = io.BytesIO(data)
        for i in range(32):
            self._players[i].name = _read_var_str(stream, 24)
        for i in range(32):
            self._players[i].hwid = _read_bytes(stream, 12)
        for i in range(32):
            self._players[i].team = PlayerTeam(_read_u8(stream))
        for i in range(32):
            self._players[i].kills = _read_u16_le(stream)
        for i in range(32):
            self._players[i].caps = _read_u8(stream)
        for i in range(32):
            self._players[i].deaths = _read_u16_le(stream)
        for i in range(32):
            self._players[i].ping = _read_u32_le(stream)
        for i in range(32):
            self._players[i].id = _read_u8(stream)
        for i in range(32):
            self._players[i].ip = '.'.join(
                str(octet) for octet in [_read_u8(stream) for i in range(4)])
        for i in range(32):
            self._players[i].pos.x = _read_f32(stream)
        for i in range(32):
            self._players[i].pos.y = _read_f32(stream)

        self.red_flag_pos.x = _read_f32(stream)
        self.red_flag_pos.y = _read_f32(stream)
        self.blue_flag_pos.x = _read_f32(stream)
        self.blue_flag_pos.y = _read_f32(stream)
        for team in (
                PlayerTeam.ALPHA,
                PlayerTeam.BRAVO,
                PlayerTeam.CHARLIE,
                PlayerTeam.DELTA):
            self.scores[team] = _read_u16_le(stream)
        self.map_name = _read_var_str(stream, 16)
        self.time_limit = _read_u32_le(stream)
        self.time_left = _read_u32_le(stream)
        self.score_limit = _read_u16_le(stream)
        self.game_mode = GameMode(_read_u8(stream))
        self.max_players = _read_u8(stream)
        self.max_spectators = _read_u8(stream)
        self.game_passworded = bool(_read_u8(stream))
        self.next_map_name = _read_var_str(stream, 16)


class State:
    def __init__(self) -> None:
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

    def on_refreshx(self) -> None:
        print('Refresh x')
        print(self.game_info.map_name)


class Connection:
    def __init__(
            self, state: State, host: str, port: int, password: str) -> None:
        self.state = state
        self.host = host
        self.port = port
        self.password = password

        self._connected = False
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._tasks: List[asyncio.Future] = []

    async def connect(self, loop: asyncio.AbstractEventLoop) -> None:
        for task in self._tasks:
            task.cancel()
        self._tasks = [
            asyncio.ensure_future(
                self._looped(lambda: self._connect(loop)), loop=loop),
            asyncio.ensure_future(self._looped(self._refresh), loop=loop),
            asyncio.ensure_future(self._looped(self._read), loop=loop),
        ]

    async def close(self) -> None:
        for task in self._tasks:
            task.cancel()
            await task

    async def _looped(self, func: Callable[[], Awaitable[None]]) -> None:
        def disconnect() -> None:
            # notify only once
            if self._connected:
                self._connected = False
                self._writer = self._reader = None
                self.state.on_disconnect()

        while True:
            try:
                await func()
            except ConnectionResetError:
                disconnect()
                await asyncio.sleep(POLL_INTERVAL)
            except asyncio.CancelledError:
                disconnect()
                break

    async def _connect(self, loop: asyncio.AbstractEventLoop) -> None:
        if self._connected:
            await asyncio.sleep(POLL_INTERVAL)
            return
        self._reader, self._writer = (
            await asyncio.open_connection(self.host, self.port, loop=loop))
        self._writer.write('{}\r\n'.format(self.password).encode())
        await self._writer.drain()
        self.state.on_connect()
        self._connected = True

    async def _refresh(self) -> None:
        if self._connected:
            assert self._writer
            self._writer.write('REFRESHX\r\n'.encode())
            await self._writer.drain()
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(POLL_INTERVAL)

    async def _read(self) -> None:
        if not self._connected:
            await asyncio.sleep(POLL_INTERVAL)
            return
        assert self._reader
        line = (await self._reader.readline()).decode('latin-1').rstrip('\r\n')
        if line == 'REFRESH':
            # we're not interested in insufficient data
            _ = await self._reader.readexactly(1188)
        elif line == 'REFRESHX':
            data = await self._reader.readexactly(1992)
            self.state.game_info.update_from_refreshx_packet(data)
            self.state.on_refreshx()
        else:
            self.state.on_message(line)


async def connect(
        loop: asyncio.AbstractEventLoop,
        host: str,
        port: int,
        password: str) -> Connection:
    state = State()
    connection = Connection(state, host, port, password)
    await connection.connect(loop)
    return connection
