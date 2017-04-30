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


MAP_NAMES = [
    'Aero',
    'Airpirates',
    'Arena2',
    'Arena3',
    'Arena',
    'Bigfalls',
    'Blox',
    'Bridge',
    'Bunker',
    'Cambodia',
    'CrackedBoot',
    'ctf_Ash',
    'ctf_B2b',
    'ctf_Blade',
    'ctf_Campeche',
    'ctf_Cobra',
    'ctf_Crucifix',
    'ctf_Death',
    'ctf_Division',
    'ctf_Dropdown',
    'ctf_Equinox',
    'ctf_Guardian',
    'ctf_Hormone',
    'ctf_IceBeam',
    'ctf_Kampf',
    'ctf_Lanubya',
    'ctf_Laos',
    'ctf_Mayapan',
    'ctf_Maya',
    'ctf_MFM',
    'ctf_Nuubia',
    'ctf_Raspberry',
    'ctf_Rotten',
    'ctf_Ruins',
    'ctf_Run',
    'ctf_Scorpion',
    'ctf_Snakebite',
    'ctf_Steel',
    'ctf_Triumph',
    'ctf_Viet',
    'ctf_Voland',
    'ctf_Wretch',
    'ctf_X',
    'Daybreak',
    'DesertWind',
    'Factory',
    'Flashback',
    'HH',
    'htf_Arch',
    'htf_Baire',
    'htf_Boxed',
    'htf_Desert',
    'htf_Dorothy',
    'htf_Dusk',
    'htf_Erbium',
    'htf_Feast',
    'htf_Mossy',
    'htf_Muygen',
    'htf_Niall',
    'htf_Nuclear',
    'htf_Prison',
    'htf_Rubik',
    'htf_Star',
    'htf_Tower',
    'htf_Void',
    'htf_Vortex',
    'htf_Zajacz',
    'inf_Abel',
    'inf_April',
    'inf_Argy',
    'inf_Belltower',
    'inf_Biologic',
    'inf_Changeling',
    'inf_Flute',
    'inf_Fortress',
    'inf_Industrial',
    'inf_Messner',
    'inf_Moonshine',
    'inf_Motheaten',
    'inf_Outpost',
    'inf_Rescue',
    'inf_Rise',
    'inf_Warehouse',
    'inf_Warlock',
    'Island2k5',
    'Jungle',
    'Krab',
    'Lagrange',
    'Leaf',
    'MrSnowman',
    'RatCave',
    'Rok',
    'RR',
    'Shau',
    'Tropiccave',
    'Unlim',
    'Veoto',
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

        if not prefix:
            for command in SERVER_COMMANDS:
                if command.lower().startswith(infix.lower()):
                    yield command + (suffix or ' ')

        if prefix.strip().lower() == '/map':
            for map_name in MAP_NAMES:
                if map_name.lower().startswith(infix.lower()):
                    yield prefix + map_name + suffix
