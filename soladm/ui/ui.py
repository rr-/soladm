import asyncio
from datetime import datetime
from typing import Optional
import urwid
from soladm import net
from soladm.ui import common
from soladm.ui.command_input import CommandInput
from soladm.ui.game_stats import GameStats
from soladm.ui.player_stats import PlayerStats


class MainWidget(urwid.Columns):
    def __init__(self, game_info: net.GameInfo) -> None:
        self.stats_table = GameStats()
        self.players_table = PlayerStats()
        self.log_box = common.ExtendedListBox(urwid.SimpleListWalker([]))
        self.input_box = CommandInput(game_info)
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
            urwid.LineBox(
                urwid.Pile([self.log_box, (urwid.PACK, self.input_box)]),
                title='Console'),
        ])
        self.contents[1][0].original_widget.set_focus(1)
        self.set_focus(1)

    def keypress(self, size: common.Size, key: str) -> Optional[str]:
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
        self._refreshed = False

        self._main_widget = MainWidget(self._connection.game_info)
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

    def _on_refresh(self) -> None:
        self._main_widget.stats_table.update(self._connection.game_info)
        self._main_widget.players_table.update(self._connection.game_info)

        if self._refreshed:
            return
        self._refreshed = True
        self._log('-*- Current players:')
        for player in self._connection.game_info.players:
            fmt = '-*- {id}. {name} ({ip}, {hwid}, {kills}/{deaths})'
            if player.caps:
                fmt += ' (+{caps} caps)'
            self._log(fmt.format(
                id=player.id,
                ip=player.ip,
                name=player.name,
                hwid=player.hwid or '-',
                kills=player.kills,
                deaths=player.deaths,
                caps=player.caps))

    def _on_exception(self, exception: Exception) -> None:
        self._log('-*- Exception: {}'.format(exception))

    def _log(self, text: str) -> None:
        self._main_widget.log_box.body.append(urwid.Text('[{}] {}'.format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'), text)))
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
