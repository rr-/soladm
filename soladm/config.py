import configparser
from typing import Any, Optional, List
from pathlib import Path


_UNUSED = object()


class AutoCompleteConfig:
    def __init__(self) -> None:
        self.server_commands: List[str] = []
        self.map_names: List[str] = []
        self.bot_names: List[str] = []


class ConnectionConfig:
    def __init__(self) -> None:
        self.host: Optional[str] = None
        self.port: Optional[int] = None
        self.password: Optional[str] = None


class LogConfig:
    def __init__(self) -> None:
        self.path: Optional[str] = None


class Config:
    def __init__(self) -> None:
        self.autocomplete = AutoCompleteConfig()
        self.connection = ConnectionConfig()
        self.log = LogConfig()


_config = Config()


def _split_lines(text: str) -> List[str]:
    return [line.strip() for line in text.split('\n')]


def read_config(path: Path) -> None:
    ini = configparser.ConfigParser(interpolation=None)
    ini.read_string(path.read_text())

    tmp: Any

    tmp = ini.get('autocomplete', 'server_commands', fallback=_UNUSED)
    if tmp != _UNUSED:
        _config.autocomplete.server_commands = _split_lines(tmp)

    tmp = ini.get('autocomplete', 'map_names', fallback=_UNUSED)
    if tmp != _UNUSED:
        _config.autocomplete.map_names = _split_lines(tmp)

    tmp = ini.get('autocomplete', 'bot_names', fallback=_UNUSED)
    if tmp != _UNUSED:
        _config.autocomplete.bot_names = _split_lines(tmp)

    tmp = ini.get('server', 'host', fallback=_UNUSED)
    if tmp != _UNUSED:
        _config.connection.host = tmp

    tmp = ini.getint('server', 'port', fallback=_UNUSED)
    if tmp != _UNUSED:
        _config.connection.port = tmp

    tmp = (
        ini.get('server', 'pass', fallback=None) or
        ini.get('server', 'password', fallback=None) or
        _UNUSED)
    if tmp != _UNUSED:
        _config.connection.password = tmp

    tmp = ini.get('log', 'path', fallback=_UNUSED)
    if tmp != _UNUSED:
        _config.log.path = tmp


def get_config() -> Config:
    return _config
