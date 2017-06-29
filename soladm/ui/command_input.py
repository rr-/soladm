from typing import Optional, Tuple, List, Iterable
import enum
import urwid
import urwid_readline
from soladm import net
from soladm.ui import autocomplete


class CommandInputMode(enum.Enum):
    COMMAND = 1
    CHAT = 2


class CommandInput(urwid_readline.ReadlineEdit):
    signals = ['command', 'chat']

    def __init__(self, game_info: net.GameInfo) -> None:
        super().__init__(wrap=urwid.CLIP)
        self._mode = CommandInputMode.COMMAND
        self._game_info = game_info
        self._history_idx = -1
        self._history: List[str] = []
        self._autocomplete_idx = -1
        self._autocomplete_suggestions: List[str] = []

    def keypress(self, size: Tuple[int, int], key: str) -> Optional[str]:
        if key == 'enter':
            self._accept()
        elif key == 'ctrl p' or key == 'up':
            self._history_up()
        elif key == 'ctrl n' or key == 'down':
            self._history_down()
        elif key == 'ctrl q':
            raise KeyboardInterrupt()
        elif key == 'ctrl x':
            self._cycle_mode()
        elif key == 'tab':
            self._cycle_autocomplete(1)
        elif key == 'shift tab':
            self._cycle_autocomplete(-1)
        else:
            self._autocomplete_suggestions = []
            return super().keypress(size, key)
        return None

    @property
    def _mode(self) -> CommandInputMode:
        return self.__mode

    @_mode.setter
    def _mode(self, mode: CommandInputMode) -> None:
        self.__mode = mode
        if mode == CommandInputMode.COMMAND:
            self.set_caption('Command: ')
        elif mode == CommandInputMode.CHAT:
            self.set_caption('Chat: ')

    def _cycle_mode(self) -> None:
        modes = list(CommandInputMode)
        idx = modes.index(self._mode)
        self._mode = modes[(idx + 1) % len(modes)]

    def _cycle_autocomplete(self, delta: int) -> None:
        if not self._autocomplete_suggestions:
            self._autocomplete_suggestions = list(self._collect_autocomplete())
            self._autocomplete_idx = 0
        if not self._autocomplete_suggestions:
            return
        suggestion = self._autocomplete_suggestions[self._autocomplete_idx]
        self.set_edit_text(suggestion)
        self.set_edit_pos(len(self.edit_text))
        self._autocomplete_idx += delta
        self._autocomplete_idx %= len(self._autocomplete_suggestions)

    def _get_affixes(self) -> Iterable[Tuple[str, str, str]]:
        return autocomplete.get_affixes(self.edit_text, self.edit_pos)

    def _collect_autocomplete(self) -> Iterable[str]:
        if self._mode == CommandInputMode.COMMAND:
            return autocomplete.collect_commands(
                self._game_info.players, self._get_affixes())
        else:
            return autocomplete.collect_chat(
                self._game_info.players, self._get_affixes())

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
        if self._mode == CommandInputMode.COMMAND:
            urwid.signals.emit_signal(self, 'command', text)
        elif self._mode == CommandInputMode.CHAT:
            urwid.signals.emit_signal(self, 'chat', text)
