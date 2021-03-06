from typing import Any, Sequence, List
import urwid
from soladm import net
from soladm.ui import common


def _pad(text: str, size: int) -> str:
    return text + ' ' * max(0, size - len(text))


class PlayerStats(common.Table):
    def __init__(self) -> None:
        self._header_row = [
            urwid.Text(_pad('ID', 2)),
            urwid.Text(_pad('Nick', 24)),
            urwid.Text(_pad('Team', 9)),
            urwid.Text(_pad('Ping', 4)),
            urwid.Text(_pad('HWID', 11)),
            urwid.Text(_pad('IP', 15)),
            urwid.Text(_pad('Score', 15)),
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

        def player_sort(player: net.PlayerInfo) -> Any:
            return (player.team, player.id)

        for i, player in enumerate(sorted(game_info.players, key=player_sort)):
            cls = {
                net.PlayerTeam.NONE: 'player_list_none',
                net.PlayerTeam.ALPHA: 'player_list_alpha',
                net.PlayerTeam.BRAVO: 'player_list_bravo',
                net.PlayerTeam.CHARLIE: 'player_list_charlie',
                net.PlayerTeam.DELTA: 'player_list_delta',
                net.PlayerTeam.SPECTATOR: 'player_list_spec',
            }[player.team]
            self.ids[i].set_text(str(player.id))
            self.names[i].set_text(player.name)
            self.teams[i].set_text((cls, common.format_team_name(player)))
            self.pings[i].set_text(str(player.ping))
            self.hwids[i].set_text(player.hwid or '-')
            self.ips[i].set_text(player.ip)
            self.scores[i].set_text(common.format_player_score(player))
