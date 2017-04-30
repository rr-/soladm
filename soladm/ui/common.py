from typing import Tuple, Sequence, List
import urwid


Size = Tuple[int, int]


def format_time(seconds: int) -> str:
    minutes = seconds // 60
    seconds = seconds % 60
    return '{:02}:{:02}'.format(minutes, seconds)


class TableColumn(urwid.Pile):
    def pack(self, size: Size, focus: bool = False) -> Size:
        maxcol = size[0]
        limit = max([i[0].pack((maxcol,), focus)[0] for i in self.contents])
        return (min(limit, maxcol), len(self.contents))



class Table(urwid.Columns):
    def __init__(self, column_count: int) -> None:
        columns = [(urwid.PACK, TableColumn([])) for i in range(column_count)]
        super().__init__(columns, dividechars=2)

    def clear_rows(self) -> None:
        for i in range(len(self.contents)):
            self.contents[i][0].contents.clear()

    def add_rows(self, rows: List[Sequence[urwid.Widget]]) -> None:
        for row in rows:
            self.add_row(row)

    def add_row(self, cells: Sequence[urwid.Widget]) -> None:
        for i, widget in enumerate(cells):
            self.contents[i][0].contents.append(
                (widget, (urwid.PACK, None)))

    def pack(self, size: Size, focus: bool = False) -> Size:
        maxcol = size[0]
        width = (
            sum(item[0].pack(size, focus)[0] for item in self.contents)
            + self.dividechars * (len(self.contents) - 1))
        height = sum(
            item[0].pack(size, focus)[1] for item in self.contents)
        return (width, height)


class ExtendedListBox(urwid.ListBox):
    def __init__(self, body: urwid.ListWalker) -> None:
        super().__init__(body)
        self.auto_scroll = True

    def scroll_to_bottom(self) -> None:
        if self.auto_scroll:
            self.set_focus(len(self.body) - 1)


class PackedLineBox(urwid.LineBox):
    def pack(self, size: Size, focus: bool = False) -> Size:
        width, height = self.original_widget.pack(size, focus)
        width2, _ = self.title_widget.pack((size[0],), focus)
        return (max(width, width2) + 2, height + 2)