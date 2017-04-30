from typing import Optional, Sequence, List
import urwid
from soladm import net
from soladm.ui import common


class GameStats(common.Table):
    def __init__(self) -> None:
        super().__init__(column_count=2)

        self._shown_game_mode: Optional[net.GameMode] = None

        self.game_mode = urwid.Text('')
        self.current_map_name = urwid.Text('')
        self.next_map_name = urwid.Text('')
        self.player_count = urwid.Text('')
        self.time = urwid.Text('')
        self.max_score = urwid.Text('')
        self.team_scores_header = urwid.Text('')
        self.team_scores = {
            net.PlayerTeam.ALPHA: urwid.Text(''),
            net.PlayerTeam.BRAVO: urwid.Text(''),
            net.PlayerTeam.CHARLIE: urwid.Text(''),
            net.PlayerTeam.DELTA: urwid.Text(''),
        }

        basic_rows: List[Sequence[urwid.Widget]] = [
            [urwid.Text('Game mode'), self.game_mode],
            [urwid.Text('Map'), self.current_map_name],
            [urwid.Text('Next map'), self.next_map_name],
            [urwid.Text('Players'), self.player_count],
            [urwid.Text('Time'), self.time],
        ]
        self.add_rows(basic_rows)

        self._no_teams_rows = basic_rows + [
            [urwid.Text('Max score'), self.max_score],
        ]
        self._two_teams_rows = basic_rows + [
            [urwid.Text(''), urwid.Text('')],
            [urwid.Text('Scores'), self.team_scores_header],
            [urwid.Text('Alpha'), self.team_scores[net.PlayerTeam.ALPHA]],
            [urwid.Text('Bravo'), self.team_scores[net.PlayerTeam.BRAVO]],
        ]
        self._four_teams_rows = self._two_teams_rows + [
            [urwid.Text('Charlie'), self.team_scores[net.PlayerTeam.CHARLIE]],
            [urwid.Text('Delta'), self.team_scores[net.PlayerTeam.DELTA]],
        ]

    def update(self, game_info: net.GameInfo) -> None:
        if self._shown_game_mode != game_info.game_mode:
            self._shown_game_mode = game_info.game_mode
            self.clear_rows()
            self.add_rows({
                net.GameMode.DeathMatch: self._no_teams_rows,
                net.GameMode.PointMatch: self._no_teams_rows,
                net.GameMode.TeamMatch: self._four_teams_rows,
                net.GameMode.CaptureTheFlag: self._two_teams_rows,
                net.GameMode.RamboMatch: self._no_teams_rows,
                net.GameMode.Infiltration: self._two_teams_rows,
                net.GameMode.HoldTheFlag: self._two_teams_rows,
            }[game_info.game_mode])

        self.game_mode.set_text({
            net.GameMode.DeathMatch: 'DM',
            net.GameMode.PointMatch: 'PM',
            net.GameMode.TeamMatch:  'TM',
            net.GameMode.CaptureTheFlag: 'CTF',
            net.GameMode.RamboMatch: 'RM',
            net.GameMode.Infiltration: 'INF',
            net.GameMode.HoldTheFlag: 'HTF',
        }[game_info.game_mode])
        self.current_map_name.set_text(game_info.map_name)
        self.next_map_name.set_text(game_info.next_map_name)
        self.player_count.set_text(
            '{}/{} ({}/{} spectators)'.format(
                len(game_info.players),
                game_info.max_players,
                len([
                    player
                    for player in game_info.players
                    if player.team == net.PlayerTeam.SPECTATOR
                ]),
                game_info.max_spectators))
        self.time.set_text(
            '{}/{} ({} left)'.format(
                common.format_time(game_info.time_elapsed // 60),
                common.format_time(game_info.time_limit // 60),
                common.format_time(game_info.time_left // 60)))
        self.team_scores_header.set_text(
            '(max: {})'.format(game_info.score_limit))
        for team in (
                net.PlayerTeam.ALPHA,
                net.PlayerTeam.CHARLIE,
                net.PlayerTeam.DELTA,
                net.PlayerTeam.BRAVO):
            self.team_scores[team].set_text(str(game_info.scores[team]))
