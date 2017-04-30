from typing import Optional, Tuple, List
import urwid
import urwid_readline


class CommandInput(urwid_readline.ReadlineEdit):
    signals = ['accept']

    def __init__(self) -> None:
        super().__init__('Command: ', wrap=urwid.CLIP)
        self._history_idx = -1
        self._history: List[str] = []

    def keypress(self, size: Tuple[int, int], key: str) -> Optional[str]:
        if key == 'enter':
            self._accept()
        elif key == 'ctrl p' or key == 'up':
            self._history_up()
        elif key == 'ctrl n' or key == 'down':
            self._history_down()
        else:
            return super().keypress(size, key)
        return None

    def _history_up(self) -> None:
        self._history_go(-1)

    def _history_down(self) -> None:
        self._history_go(1)

    def _history_go(self, delta: int) -> None:
        self._history_idx += delta
        if self._history_idx not in range(len(self._history)):
            self.set_edit_text('')
        else:
            self.set_edit_text(self._history[self._history_idx])
            self.set_edit_pos(len(self.edit_text))
        if self._history_idx < -1:
            self._history_idx = -1
        if self._history_idx > len(self._history):
            self._history_idx = len(self._history)

    def _accept(self) -> None:
        text = self.edit_text.strip()
        if not text:
            return
        self.set_edit_text('')
        self._history.append(text)
        self._history_idx = len(self._history)
        urwid.signals.emit_signal(self, 'accept', text)
