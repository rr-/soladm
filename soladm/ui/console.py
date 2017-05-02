from typing import Optional
import urwid
from soladm import net
from soladm.ui import common
from soladm.ui.command_input import CommandInput


class Console(urwid.Pile):
    def __init__(self, game_info: net.GameInfo) -> None:
        self.log_box = common.ExtendedListBox(urwid.SimpleListWalker([]))
        self.input_box = CommandInput(game_info)
        super().__init__([self.log_box, (urwid.PACK, self.input_box)])

    def keypress(self, size: common.Size, key: str) -> Optional[str]:
        if key == 'meta b':
            return self.keypress(size, 'page up')
        if key == 'meta f':
            return self.keypress(size, 'page down')
        if key in ('page up', 'page down'):
            return self.log_box.keypress(
                self.get_item_size(size, 0, False), key)
        return self.input_box.keypress(self.get_item_size(size, 1, True), key)
