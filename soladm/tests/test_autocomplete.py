from typing import Tuple, Iterable
import pytest
from soladm.ui import autocomplete


@pytest.mark.parametrize('edit_text,edit_pos,affixes', [
    ('', 0, [('', '', '')]),
    ('abc', 0, [('', '', 'abc')]),
    ('abc def', 0, [('', '', 'abc def')]),
    ('abc', 2, [('', 'ab', 'c')]),
    ('ab ', 2, [('', 'ab', ' ')]),
    ('  c', 2, [('', '  ', 'c')]),
    (' bc', 2, [('', ' b', 'c'), (' ', 'b', 'c')]),
    ('a c', 2, [('', 'a ', 'c')]),

    ('abc def', 5, [
        ('', 'abc d', 'ef'),
        ('abc ', 'd', 'ef'),
    ]),
    ('a c def', 5, [
        ('', 'a c d', 'ef'),
        ('a ', 'c d', 'ef'),
        ('a c ', 'd', 'ef'),
    ]),
])
def test_get_affixes(
        edit_text: str,
        edit_pos: int,
        affixes: Iterable[Tuple[str, str, str]]) -> None:
    assert autocomplete.get_affixes(edit_text, edit_pos) == affixes
