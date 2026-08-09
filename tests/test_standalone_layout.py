"""Static screen-contract checks for the embedded Mystic door."""

import ast
from pathlib import Path


TARGET = Path(__file__).parents[1] / "integrations/mystic/standalone/ansiradar.mpy"


def tree():
    return ast.parse(TARGET.read_text(encoding="ascii"), filename=str(TARGET))


def constants():
    values = {}
    for node in tree().body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                try:
                    values[target.id] = ast.literal_eval(node.value)
                except ValueError:
                    pass
    return values


def test_output_source_is_ascii_and_screen_is_safe_area():
    raw = TARGET.read_bytes()
    raw.decode("ascii")
    values = constants()
    assert values["SCREEN_WIDTH"] == 79
    assert values["SCREEN_HEIGHT"] == 24
    assert values["RADAR_TOP"] == 2
    assert values["RADAR_BOTTOM"] == 13
    assert values["RADAR_CENTER_ROW"] == 8


def test_literal_put_rows_never_target_row_25_or_later():
    for node in ast.walk(tree()):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        if node.func.id != "put" or len(node.args) < 2:
            continue
        row = node.args[1]
        if isinstance(row, ast.Constant) and isinstance(row.value, int):
            assert 0 <= row.value < 24


def test_static_text_lines_fit_the_printable_screen_width():
    for node in ast.walk(tree()):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            for line in node.value.splitlines():
                assert len(line) <= 79, repr(line)


def test_renderer_uses_fixed_width_rows_and_no_cleanup_exit():
    source = TARGET.read_text(encoding="ascii")
    assert "[list(\" \" * SCREEN_WIDTH) for unused in range(SCREEN_HEIGHT)]" in source
    assert "screen_output(screen, colours)" in source
    assert "output += screen_output(screen, colours)" in source
    assert "ESC + \"2J\" + ESC + \"H\"" in source
    assert "ESC + \"c\"" not in source
