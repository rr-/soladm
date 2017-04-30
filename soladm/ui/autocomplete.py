import re
from typing import Tuple, List, Iterable
from soladm import net


SERVER_COMMANDS = [
    '/addbot',
    '/addbot1',
    '/addbot2',
    '/addbot3',
    '/addbot4',
    '/map',
    '/nextmap',
    '/restart',
    '/pause',
    '/unpause',
    '/kick',
    '/kicklast',
    '/ban',
    '/banlast',
    '/banip',
    '/banhw',
    '/unban',
    '/unbanhw',
    '/unbanlast',
    '/admip',
    '/adm',
    '/unadm',
    '/respawntime',
    '/minrespawntime',
    '/maxrespawntime',
    '/limit',
    '/maxgrenades',
    '/bonus',
    '/timelimit',
    '/maxplayers',
    '/friendlyfire',
    '/password',
    '/vote%',
    '/say',
    '/setteam',
    '/setteam1',
    '/setteam2',
    '/setteam3',
    '/setteam4',
    '/loadwep',
    '/gamemode',
    '/realistic',
    '/survival',
    '/advance',
    '/kill',
    '/loadcon',
    '/loadlist',
    '/lobby',
    '/pm',
    '/gmute',
    '/ungmute',
    '/addmap',
    '/delmap',
    '/balance',
    '/tempban',
    '/bandwidth',
    '/recompile',
    '/welcome',
    '/weaponon',
    '/weaponoff',
    '/scripting'
]


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


def collect(
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

        for command in SERVER_COMMANDS:
            if prefix == '' and command.lower().startswith(infix.lower()):
                if suffix:
                    yield command + suffix
                else:
                    yield command + ' '
