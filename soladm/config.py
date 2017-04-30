import configparser
from typing import List
from pathlib import Path


class AutoCompleteConfig:
    def __init__(self) -> None:
        self.server_commands: List[str] = []
        self.map_names: List[str] = []
        self.bot_names: List[str] = []


class Config:
    def __init__(self) -> None:
        self.autocomplete = AutoCompleteConfig()


_config = Config()


def _split_lines(text: str) -> List[str]:
    return [line.strip() for line in text.split('\n')]


def read_config(path: Path):
    ini = configparser.ConfigParser(interpolation=None)
    ini.read_string(path.read_text())

    _config.autocomplete.server_commands = _split_lines(
        ini.get('autocomplete', 'server_commands', fallback=''))
    _config.autocomplete.map_names = _split_lines(
        ini.get('autocomplete', 'map_names', fallback=''))
    _config.autocomplete.bot_names = _split_lines(
        ini.get('autocomplete', 'bot_names', fallback=''))


def get_config() -> Config:
    return _config
