import asyncio
from datetime import datetime
from typing import Optional
from pathlib import Path
import urwid
from soladm import net
from soladm import config
from soladm.ui import common
from soladm.ui.console import Console
from soladm.ui.game_stats import GameStats
from soladm.ui.player_stats import PlayerStats


class MainWidget(urwid.Columns):
    def __init__(self, game_info: net.GameInfo) -> None:
        self.stats_table = GameStats()
        self.players_table = PlayerStats()
        self.console = Console(game_info)
        super().__init__([
            (
                urwid.PACK,
                common.TableColumn([
                    (
                        urwid.PACK,
                        common.PackedLineBox(
                            self.stats_table, title='Game stats')
                    ),
                    common.PackedLineBox(self.players_table, title='Players'),
                ]),
            ),
            urwid.LineBox(self.console, title='Console'),
        ])
        self.contents[1][0].original_widget.set_focus(1)
        self.set_focus(1)


class Ui:
    def __init__(
            self,
            connection: net.Connection,
            log_path: Optional[Path]) -> None:
        self._connection = connection
        self._connection.on_connecting.append(self._on_connecting)
        self._connection.on_connect.append(self._on_connect)
        self._connection.on_disconnect.append(self._on_disconnect)
        self._connection.on_message.append(self._on_message)
        self._connection.on_refresh.append(self._on_refresh)
        self._connection.on_exception.append(self._on_exception)
        self._refreshed = False
        self._log_path = log_path
        self._config = config.get_config()

        self._main_widget = MainWidget(self._connection.game_info)
        urwid.signals.connect_signal(
            self._main_widget.console.input_box,
            'accept',
            self._command_accept)
        self._loop = urwid.MainLoop(
            self._main_widget, event_loop=urwid.AsyncioEventLoop())
        self._loop.screen.set_terminal_properties(256)

    def start(self) -> None:
        self._loop.start()

    def stop(self) -> None:
        self._loop.stop()

    def _command_accept(self, text: str) -> None:
        asyncio.ensure_future(self._connection.send(text))

    def _on_connecting(self) -> None:
        self._log('-*- Connecting to {}:{}...'.format(
            self._connection.host, self._connection.port))

    def _on_connect(self) -> None:
        self._log('-*- Connected')

    def _on_disconnect(self, reason: str) -> None:
        self._log('-*- Disconnected ({})'.format(reason))

    def _on_message(self, message: str) -> None:
        self._log(message)

    def _on_refresh(self) -> None:
        self._main_widget.stats_table.update(self._connection)
        self._main_widget.players_table.update(self._connection.game_info)

        if self._refreshed:
            return
        self._refreshed = True
        self._log('-*- Current players:')
        if self._connection.game_info.players:
            max_nick_length = max(
                len(player.name)
                for player in self._connection.game_info.players)
            for player in self._connection.game_info.players:
                fmt = (
                    '-*- {id}. {name:%d} (IP: {ip}, HWID: {hwid}, '
                    'team: {team}, score: {score})' % max_nick_length)
                self._log(fmt.format(
                    id=player.id,
                    ip=player.ip,
                    name=player.name,
                    hwid=player.hwid or '-',
                    team=common.format_team_name(player),
                    score=common.format_player_score(player)))
        else:
            self._log('-*- (no players)')

    def _on_exception(self, exception: Exception) -> None:
        self._log('-*- Exception: {} ({})'.format(type(exception), exception))

    def _log(self, text: str) -> None:
        timestamp_prefix = datetime.now().strftime('%Y-%m-%d %H:%M:%S ')
        self._log_to_ui(timestamp_prefix, text)
        self._log_to_file(timestamp_prefix, text)

    def _log_to_file(self, prefix: str, text: str) -> None:
        if not self._log_path:
            return
        try:
            with self._log_path.open('a', encoding='utf-8') as handle:
                handle.write(prefix + text + '\n')
        except Exception as ex:
            self._log_to_ui('~*~ Error writing log file: {}'.format(ex))

    def _log_to_ui(self, prefix: str, text: str) -> None:
        for pattern in self._config.ui.filter_regexes:
            if pattern.match(text):
                return
        self._main_widget.console.log_box.body.append(
            urwid.Text(prefix + text))
        self._main_widget.console.log_box.scroll_to_bottom()


def run(connection: net.Connection, log_path: Optional[Path]) -> None:
    ui = Ui(connection, log_path)
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
