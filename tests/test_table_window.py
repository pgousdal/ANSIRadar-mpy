"""Behavior checks for the standalone aircraft table window."""

import ast
from pathlib import Path


TARGET = Path(__file__).parents[1] / "integrations/mystic/standalone/ansiradar.mpy"


def table_window():
    tree = ast.parse(TARGET.read_text(encoding="ascii"), filename=str(TARGET))
    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "table_window"
    )
    namespace = {}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(TARGET), "exec"), namespace)
    return namespace["table_window"]


def test_table_window_keeps_first_and_last_items_normal():
    window = table_window()
    items = list(range(7))

    assert window(items, 0, 3) == ([0, 1, 2], 0)
    assert window(items, 6, 3) == ([4, 5, 6], 4)


def test_table_window_keeps_selection_visible_while_scrolling():
    window = table_window()
    items = list(range(7))

    for selected in range(len(items)):
        visible, start = window(items, selected, 3)
        assert items[selected] in visible
        assert visible == items[start:start + 3]

    assert window(items, 1, 3) == ([0, 1, 2], 0)
    assert window(items, 2, 3) == ([1, 2, 3], 1)


def test_table_window_handles_empty_and_unusable_sizes():
    window = table_window()

    assert window([], 0, 3) == ([], 0)
    assert window([1, 2], 0, 0) == ([], 0)
