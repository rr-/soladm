import asyncio
from typing import Optional, Tuple
import urwid
import urwid_readline
from soladm import net


class ExtendedListBox(urwid.ListBox):
    def __init__(self, body: urwid.ListWalker) -> None:
        super().__init__(body)
        self.auto_scroll = True

    def scroll_to_bottom(self) -> None:
        if self.auto_scroll:
            self.set_focus(len(self.body) - 1)


class MainWidget(urwid.Pile):
    def __init__(self) -> None:
        self.log_box = ExtendedListBox(urwid.SimpleListWalker([]))
        self.input_box = urwid_readline.ReadlineEdit('', wrap=urwid.CLIP)
        super().__init__([self.log_box, (urwid.PACK, self.input_box)])
        self.set_focus(1)

    def keypress(self, size: Tuple[int, int], key: str) -> Optional[str]:
        if key in ('page up', 'page down'):
            self.log_box.keypress(self.get_item_size(size, 0, False), key)
            self.log_box.auto_scroll = (
                self.log_box.get_focus()[1] == len(self.log_box.body) - 1)
            return None
        return super().keypress(size, key)


class Ui:
    def __init__(self, connection: net.Connection) -> None:
        self.connection = connection
        self.connection.on_connect.append(self._on_connect)
        self.connection.on_disconnect.append(self._on_disconnect)
        self.connection.on_message.append(self._on_message)
        self.connection.on_refresh.append(self._on_refresh)
        self.connection.on_exception.append(self._on_exception)

        self._main_widget = MainWidget()
        self._loop = urwid.MainLoop(
            self._main_widget, event_loop=urwid.AsyncioEventLoop())
        self._loop.screen.set_terminal_properties(256)

    def start(self) -> None:
        self._loop.start()

    def stop(self) -> None:
        self._loop.stop()

    def _on_connect(self) -> None:
        self._log('Connected')

    def _on_disconnect(self, reason: str) -> None:
        self._log('Disconnected ({})'.format(reason))

    def _on_message(self, message: str) -> None:
        self._log('Message received: {}'.format(message))

    def _on_refresh(self, game_info: net.GameInfo) -> None:
        self._log('(Refresh) {}'.format(game_info.map_name))

    def _on_exception(self, exception: Exception) -> None:
        self._log('Exception: {}'.format(exception))

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
