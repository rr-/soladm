import configparser
from typing import Optional, List
from pathlib import Path


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

    _config.autocomplete.server_commands = _split_lines(
        ini.get('autocomplete', 'server_commands', fallback=''))
    _config.autocomplete.map_names = _split_lines(
        ini.get('autocomplete', 'map_names', fallback=''))
    _config.autocomplete.bot_names = _split_lines(
        ini.get('autocomplete', 'bot_names', fallback=''))
    _config.connection.host = ini.get('server', 'host', fallback=None)
    _config.connection.port = ini.getint('server', 'port', fallback=None)
    _config.connection.password = (
        ini.get('server', 'pass', fallback=None) or
        ini.get('server', 'password', fallback=None))
    _config.log.path = ini.get('log', 'path', fallback=None)


def get_config() -> Config:
    return _config
