import asyncio
from typing import Optional, Tuple, Sequence, List
import urwid
import urwid_readline
from soladm import net


def _format_time(seconds: int) -> str:
    minutes = seconds // 60
    seconds = seconds % 60
    return '{:02}:{:02}'.format(minutes, seconds)


class TableColumn(urwid.Pile):
    def pack(
            self,
            size: Tuple[int, int],
            focus: bool = False) -> Tuple[int, int]:
        maxcol = size[0]
        limit = max([i[0].pack((maxcol,), focus)[0] for i in self.contents])
        return (min(limit + 2, maxcol), len(self.contents))


class Table(urwid.WidgetWrap):
    def __init__(self, column_count: int) -> None:
        columns = [(urwid.PACK, TableColumn([])) for i in range(column_count)]
        super().__init__(urwid.Columns(columns))

    def clear_rows(self) -> None:
        for i in range(len(self._w.contents)):
            self._w.contents[i][0].contents.clear()

    def add_rows(self, rows: List[Sequence[urwid.Widget]]) -> None:
        for row in rows:
            self.add_row(row)

    def add_row(self, cells: Sequence[urwid.Widget]) -> None:
        for i, widget in enumerate(cells):
            self._w.contents[i][0].contents.append(
                (widget, (urwid.PACK, None)))


class CommandInput(urwid_readline.ReadlineEdit):
    signals = ['accept']

    def keypress(self, size: Tuple[int, int], key: str) -> Optional[str]:
        if key == 'enter':
            self._accept()
        return super().keypress(size, key)

    def _accept(self) -> None:
        text = self.text.strip()
        if not text:
            return
        self.set_edit_text('')
        urwid.signals.emit_signal(self, 'accept', text)


class ExtendedListBox(urwid.ListBox):
    def __init__(self, body: urwid.ListWalker) -> None:
        super().__init__(body)
        self.auto_scroll = True

    def scroll_to_bottom(self) -> None:
        if self.auto_scroll:
            self.set_focus(len(self.body) - 1)


class GameStats(Table):
    def __init__(self) -> None:
        super().__init__(column_count=2)

        self.game_mode = urwid.Text('')
        self.current_map_name = urwid.Text('')
        self.next_map_name = urwid.Text('')
        self.player_count = urwid.Text('')
        self.time = urwid.Text('')
        self.scores_header = urwid.Text('')
        self.scores = {
            net.PlayerTeam.ALPHA: urwid.Text(''),
            net.PlayerTeam.BRAVO: urwid.Text(''),
            net.PlayerTeam.CHARLIE: urwid.Text(''),
            net.PlayerTeam.DELTA: urwid.Text(''),
        }

        self.add_rows([
            [urwid.Text('Game mode'), self.game_mode],
            [urwid.Text('Map'), self.current_map_name],
            [urwid.Text('Next map'), self.next_map_name],
            [urwid.Text('Players'), self.player_count],
            [urwid.Text('Time'), self.time],
            [urwid.Text(''), urwid.Text('')],
            [urwid.Text('Scores'), self.scores_header],
            [urwid.Text('Alpha'), self.scores[net.PlayerTeam.ALPHA]],
            [urwid.Text('Bravo'), self.scores[net.PlayerTeam.BRAVO]],
            [urwid.Text('Charlie'), self.scores[net.PlayerTeam.CHARLIE]],
            [urwid.Text('Delta'), self.scores[net.PlayerTeam.DELTA]],
        ])

    def update(self, game_info: net.GameInfo) -> None:
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
                _format_time(game_info.time_elapsed // 60),
                _format_time(game_info.time_limit // 60),
                _format_time(game_info.time_left // 60)))
        self.scores_header.set_text(
            '(max: {})'.format(game_info.score_limit))
        for team in (
                net.PlayerTeam.ALPHA,
                net.PlayerTeam.CHARLIE,
                net.PlayerTeam.DELTA,
                net.PlayerTeam.BRAVO):
            self.scores[team].set_text(str(game_info.scores[team]))


class PlayerStats(Table):
    def __init__(self) -> None:
        super().__init__(column_count=7)
        self.add_row([
            urwid.Text('ID'),
            urwid.Text('Nick'),
            urwid.Text('Team'),
            urwid.Text('Ping'),
            urwid.Text('HWID'),
            urwid.Text('IP'),
            urwid.Text('Score'),
        ])
        self.ids = [urwid.Text('') for i in range(net.MAX_PLAYERS)]
        self.names = [urwid.Text('') for i in range(net.MAX_PLAYERS)]
        self.teams = [urwid.Text('') for i in range(net.MAX_PLAYERS)]
        self.pings = [urwid.Text('') for i in range(net.MAX_PLAYERS)]
        self.hwids = [urwid.Text('') for i in range(net.MAX_PLAYERS)]
        self.ips = [urwid.Text('') for i in range(net.MAX_PLAYERS)]
        self.scores = [urwid.Text('') for i in range(net.MAX_PLAYERS)]

        for i in range(net.MAX_PLAYERS):
            self.add_row([
                self.ids[i],
                self.names[i],
                self.teams[i],
                self.pings[i],
                self.hwids[i],
                self.ips[i],
                self.scores[i],
            ])

    def update(self, game_info: net.GameInfo) -> None:
        for i, player in enumerate(game_info.players):
            self.ids[i].set_text(str(player.id))
            self.names[i].set_text(player.name)
            self.teams[i].set_text({
                net.PlayerTeam.NONE: 'none',
                net.PlayerTeam.ALPHA: 'alpha',
                net.PlayerTeam.BRAVO: 'bravo',
                net.PlayerTeam.CHARLIE: 'charlie',
                net.PlayerTeam.DELTA: 'delta',
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


class MainWidget(urwid.Pile):
    def __init__(self) -> None:
        self.stats_table = GameStats()
        self.players_table = PlayerStats()
        self.log_box = ExtendedListBox(urwid.SimpleListWalker([]))
        self.input_box = CommandInput('', wrap=urwid.CLIP)
        super().__init__([
            (
                urwid.PACK,
                urwid.Columns([
                    urwid.LineBox(self.stats_table, title='Game stats'),
                    urwid.LineBox(self.players_table, title='Players'),
                ]),
            ),
            self.log_box,
            (urwid.PACK, self.input_box)])
        self.set_focus(2)

    def keypress(self, size: Tuple[int, int], key: str) -> Optional[str]:
        if key in ('page up', 'page down'):
            self.log_box.keypress(self.get_item_size(size, 0, False), key)
            self.log_box.auto_scroll = (
                self.log_box.get_focus()[1] == len(self.log_box.body) - 1)
            return None
        return super().keypress(size, key)


class Ui:
    def __init__(self, connection: net.Connection) -> None:
        self._connection = connection
        self._connection.on_connect.append(self._on_connect)
        self._connection.on_disconnect.append(self._on_disconnect)
        self._connection.on_message.append(self._on_message)
        self._connection.on_refresh.append(self._on_refresh)
        self._connection.on_exception.append(self._on_exception)

        self._main_widget = MainWidget()
        urwid.signals.connect_signal(
            self._main_widget.input_box, 'accept', self._command_accept)
        self._loop = urwid.MainLoop(
            self._main_widget, event_loop=urwid.AsyncioEventLoop())
        self._loop.screen.set_terminal_properties(256)

    def start(self) -> None:
        self._loop.start()

    def stop(self) -> None:
        self._loop.stop()

    def _command_accept(self, text: str) -> None:
        asyncio.ensure_future(self._connection.send(text))

    def _on_connect(self) -> None:
        self._log('-*- Connected')

    def _on_disconnect(self, reason: str) -> None:
        self._log('-*- Disconnected ({})'.format(reason))

    def _on_message(self, message: str) -> None:
        self._log(message)

    def _on_refresh(self, game_info: net.GameInfo) -> None:
        self._main_widget.stats_table.update(game_info)
        self._main_widget.players_table.update(game_info)

    def _on_exception(self, exception: Exception) -> None:
        self._log('-*- Exception: {}'.format(exception))

    def _log(self, text: str) -> None:
        self._main_widget.log_box.body.append(urwid.Text(text))
        self._main_widget.log_box.scroll_to_bottom()


def run(connection: net.Connection) -> None:
    ui = Ui(connection)
    ui.start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connection.open())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    loop.run_until_complete(connection.close())
    ui.stop()
    loop.close()
