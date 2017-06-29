import re
from typing import Tuple, List, Iterable
from soladm import net
from soladm.config import config


def get_affixes(
        edit_text: str,
        edit_pos: int) -> List[Tuple[str, str, str]]:
    ret: List[Tuple[str, str, str]] = []
    text = edit_text[0:edit_pos]
    suffix = edit_text[edit_pos:]
    regex = re.compile(r'\s+')
    for match in regex.finditer(text):
        pos = match.end()
        prefix = text[:pos]
        infix = text[pos:]
        if infix and prefix:
            ret.insert(0, (prefix, infix, suffix))
    ret.append(('', text, suffix))
    return list(reversed(ret))


def collect_commands(
        players: Iterable[net.PlayerInfo],
        affixes: Iterable[Tuple[str, str, str]]) -> Iterable[str]:
    for prefix, infix, suffix in affixes:
        if not infix:
            continue

        for player in players:
            if prefix == '' and \
                    player.name.lower().startswith(infix.lower()):
                yield '/say {}: {}'.format(player.name, suffix)
            if prefix != '' and \
                    player.name.lower().startswith(infix.lower()):
                yield prefix + player.name + suffix

        if not prefix:
            for command in config.autocomplete.server_commands:
                if command.lower().startswith(infix.lower()):
                    yield command + (suffix or ' ')

        elif prefix.strip().lower() == '/map':
            for map_name in config.autocomplete.map_names:
                if map_name.lower().startswith(infix.lower()):
                    yield prefix + map_name + suffix

        elif prefix.strip().lower() in (
                '/addbot', '/addbot1', '/addbot2', '/addbot3', '/addbot4'):
            for bot_name in config.autocomplete.bot_names:
                if bot_name.lower().startswith(infix.lower()):
                    yield prefix + bot_name + suffix


def collect_chat(
        players: Iterable[net.PlayerInfo],
        affixes: Iterable[Tuple[str, str, str]]) -> Iterable[str]:
    for prefix, infix, suffix in affixes:
        if not infix:
            continue
        for player in players:
            if prefix == '' and \
                    player.name.lower().startswith(infix.lower()):
                yield '{}: {}'.format(player.name, suffix)
            if prefix != '' and \
                    player.name.lower().startswith(infix.lower()):
                yield prefix + player.name + suffix
