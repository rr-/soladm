import configparser
import re
from typing import Any, Optional, Tuple, Sequence, List, Dict, Pattern
from pathlib import Path


_UNUSED = object()
Palette = Dict[str, Sequence[str]]


def _make_pattern(text: str) -> Pattern:
    text = text.replace('%{PLAYER}', r'([ -~]{1,24})')
    text = text.replace('%{HWID}', '([0-9A-Fa-f]{11})')
    text = text.replace(
        '%{IP}',
        r'((([1-9]?\d|1\d\d|25[0-5]|2[0-4]\d)\.){3}'
        r'([1-9]?\d|1\d\d|25[0-5]|2[0-4]\d))')
    text = text.replace(
        '%{PORT}',
        r'([1-9]\d{0,3}|[1-5][0-9]{4}|'
        r'6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])')
    return re.compile(text, re.I)


def _split_lines(text: str) -> List[str]:
    return [line.strip() for line in text.split('\n') if line.strip()]


def _split_dict(text: str) -> List[Tuple[str, str]]:
    ret: List[Tuple[str, str]] = []
    for line in _split_lines(text):
        key, value = line.split(':', 1)
        ret.append((key, value.lstrip()))
    return ret


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
        self.color_assignment_regexes: List[Tuple[str, Pattern]] = {}
        self.color_schemes: Dict[str, Palette] = {}
        self.colors: Palette = {}

    def read(self, ini: configparser.ConfigParser) -> None:
        tmp: Any

        tmp = ini.getint('ui', 'last_log', fallback=_UNUSED)
        if tmp != _UNUSED:
            self.last_log = tmp

        tmp = ini.get('ui', 'filter_regexes', fallback=_UNUSED)
        if tmp != _UNUSED:
            self.filter_regexes = [
                _make_pattern(line) for line in _split_lines(tmp)]

        tmp = ini.get('ui', 'bell_regexes', fallback=_UNUSED)
        if tmp != _UNUSED:
            self.bell_regexes = [
                _make_pattern(line) for line in _split_lines(tmp)]

        tmp = ini.get('ui', 'color_assignment_regexes', fallback=_UNUSED)
        if tmp != _UNUSED:
            self.color_assignment_regexes = [
                (key, _make_pattern(line))
                for key, line in _split_dict(tmp)]

        CS_PREFIX = 'ui.colors.'
        for section_name, section in ini.items():
            if section_name.startswith(CS_PREFIX):
                scheme_name = section_name.replace(CS_PREFIX, '')
                palette: Palette = {}
                for key, value in section.items():
                    palette[key] = value.split(':')
                self.color_schemes[scheme_name] = palette

        tmp = ini.get('ui', 'color_scheme', fallback=_UNUSED)
        if tmp != _UNUSED:
            self.colors = self.color_schemes[tmp]


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
