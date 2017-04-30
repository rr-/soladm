from typing import Sequence, List
import urwid
from soladm import net
from soladm.ui import common


class PlayerStats(common.Table):
    def __init__(self) -> None:
        self._header_row = [
            urwid.Text('ID'),
            urwid.Text('Nick'),
            urwid.Text('Team'),
            urwid.Text('Ping'),
            urwid.Text('HWID'),
            urwid.Text('IP'),
            urwid.Text('Score'),
        ]

        super().__init__(column_count=len(self._header_row))
        self.add_row(self._header_row)

        self.ids = [urwid.Text('') for i in range(net.MAX_PLAYERS)]
        self.names = [urwid.Text('') for i in range(net.MAX_PLAYERS)]
        self.teams = [urwid.Text('') for i in range(net.MAX_PLAYERS)]
        self.pings = [urwid.Text('') for i in range(net.MAX_PLAYERS)]
        self.hwids = [urwid.Text('') for i in range(net.MAX_PLAYERS)]
        self.ips = [urwid.Text('') for i in range(net.MAX_PLAYERS)]
        self.scores = [urwid.Text('') for i in range(net.MAX_PLAYERS)]

        self._visible_rows: List[Sequence[urwid.Widget]] = []
        self._all_rows: List[Sequence[urwid.Widget]] = []
        for i in range(net.MAX_PLAYERS):
            self._all_rows.append([
                self.ids[i],
                self.names[i],
                self.teams[i],
                self.pings[i],
                self.hwids[i],
                self.ips[i],
                self.scores[i],
            ])

    def update(self, game_info: net.GameInfo) -> None:
        if len(self._visible_rows) != len(game_info.players):
            self._visible_rows = self._all_rows[0:len(game_info.players)]
            self.clear_rows()
            self.add_row(self._header_row)
            self.add_rows(self._visible_rows)

        for i, player in enumerate(game_info.players):
            self.ids[i].set_text(str(player.id))
            self.names[i].set_text(player.name)
            self.teams[i].set_text({
                net.PlayerTeam.NONE:      'none',
                net.PlayerTeam.ALPHA:     'alpha',
                net.PlayerTeam.BRAVO:     'bravo',
                net.PlayerTeam.CHARLIE:   'charlie',
                net.PlayerTeam.DELTA:     'delta',
                net.PlayerTeam.SPECTATOR: 'spectator',
            }[player.team])
            self.pings[i].set_text(str(player.ping))
            self.hwids[i].set_text(player.hwid)
            self.ips[i].set_text(player.ip)
            self.scores[i].set_text(
                (
                    '{kills}/{deaths} (+{caps} caps)'
                    if player.caps
                    else '{kills}/{deaths}'
                ).format(
                    kills=player.kills,
                    deaths=player.deaths,
                    caps=player.caps))
