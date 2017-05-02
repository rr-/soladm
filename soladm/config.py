import configparser
import re
from typing import Any, Optional, List, Pattern
from pathlib import Path


_UNUSED = object()


def _split_lines(text: str) -> List[str]:
    return [line.strip() for line in text.split('\n') if line.strip()]


class AutoCompleteConfig:
    def __init__(self) -> None:
        self.server_commands: List[str] = []
        self.map_names: List[str] = []
        self.bot_names: List[str] = []

    def read(self, ini: configparser.ConfigParser) -> None:
        tmp: Any

        tmp = ini.get('autocomplete', 'server_commands', fallback=_UNUSED)
        if tmp != _UNUSED:
            self.server_commands = _split_lines(tmp)

        tmp = ini.get('autocomplete', 'map_names', fallback=_UNUSED)
        if tmp != _UNUSED:
            self.map_names = _split_lines(tmp)

        tmp = ini.get('autocomplete', 'bot_names', fallback=_UNUSED)
        if tmp != _UNUSED:
            self.bot_names = _split_lines(tmp)


class ConnectionConfig:
    def __init__(self) -> None:
        self.host: Optional[str] = None
        self.port: Optional[int] = None
        self.password: Optional[str] = None

    def read(self, ini: configparser.ConfigParser) -> None:
        tmp: Any

        tmp = ini.get('server', 'host', fallback=_UNUSED)
        if tmp != _UNUSED:
            self.host = tmp

        tmp = ini.getint('server', 'port', fallback=_UNUSED)
        if tmp != _UNUSED:
            self.port = tmp

        tmp = (
            ini.get('server', 'pass', fallback=None) or
            ini.get('server', 'password', fallback=None) or
            _UNUSED)
        if tmp != _UNUSED:
            self.password = tmp


class LogConfig:
    def __init__(self) -> None:
        self.path: Optional[str] = None

    def read(self, ini: configparser.ConfigParser) -> None:
        tmp: Any

        tmp = ini.get('log', 'path', fallback=_UNUSED)
        if tmp != _UNUSED:
            self.path = tmp


class UiConfig:
    def __init__(self) -> None:
        self.last_log: int = 0
        self.filter_regexes: List[Pattern] = []
        self.bell_regexes: List[Pattern] = []

    def read(self, ini: configparser.ConfigParser) -> None:
        tmp: Any

        tmp = ini.getint('ui', 'last_log', fallback=_UNUSED)
        if tmp != _UNUSED:
            self.last_log = tmp

        tmp = ini.get('ui', 'filter_regexes', fallback=_UNUSED)
        if tmp != _UNUSED:
            self.filter_regexes = [
                re.compile(line) for line in _split_lines(tmp)]

        tmp = ini.get('ui', 'bell_regexes', fallback=_UNUSED)
        if tmp != _UNUSED:
            self.bell_regexes = [
                re.compile(line) for line in _split_lines(tmp)]


class Config:
    def __init__(self) -> None:
        self.autocomplete = AutoCompleteConfig()
        self.connection = ConnectionConfig()
        self.log = LogConfig()
        self.ui = UiConfig()

    def read(self, path: Path) -> None:
        ini = configparser.ConfigParser(interpolation=None)
        ini.read_string(path.read_text())
        self.autocomplete.read(ini)
        self.connection.read(ini)
        self.log.read(ini)
        self.ui.read(ini)


config = Config()
