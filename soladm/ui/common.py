from typing import Tuple, Sequence, List
import urwid


def format_time(seconds: int) -> str:
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


class ExtendedListBox(urwid.ListBox):
    def __init__(self, body: urwid.ListWalker) -> None:
        super().__init__(body)
        self.auto_scroll = True

    def scroll_to_bottom(self) -> None:
        if self.auto_scroll:
            self.set_focus(len(self.body) - 1)
