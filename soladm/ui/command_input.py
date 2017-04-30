from typing import Optional, Tuple
import urwid
import urwid_readline


class CommandInput(urwid_readline.ReadlineEdit):
    signals = ['accept']

    def __init__(self) -> None:
        super().__init__('Command: ', wrap=urwid.CLIP)

    def keypress(self, size: Tuple[int, int], key: str) -> Optional[str]:
        if key == 'enter':
            self._accept()
        return super().keypress(size, key)

    def _accept(self) -> None:
        text = self.edit_text.strip()
        if not text:
            return
        self.set_edit_text('')
        urwid.signals.emit_signal(self, 'accept', text)
