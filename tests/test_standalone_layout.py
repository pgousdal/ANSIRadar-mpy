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
    assert values["RADAR_BOTTOM"] == 12
    assert values["RADAR_LEFT"] == 1
    assert values["RADAR_RIGHT"] == 39
    assert values["DETAILS_LEFT"] == 41
    assert values["RADAR_DIVIDER"] == 40
    assert values["RADAR_CENTER_COL"] == 21
    assert values["RADAR_CENTER_ROW"] == 7
    assert values["RADAR_RADIUS_X"] == 17
    assert values["RADAR_RADIUS_Y"] == 5


def test_literal_put_rows_never_target_row_25_or_later():
    for node in ast.walk(tree()):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        if node.func.id != "put" or len(node.args) < 2:
            continue
        row = node.args[1]
        if isinstance(row, ast.Constant) and isinstance(row.value, int):
            assert 0 <= row.value < 24


def test_literal_put_columns_never_target_column_80_or_later():
    for node in ast.walk(tree()):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        if node.func.id != "put" or len(node.args) < 3:
            continue
        column = node.args[2]
        if isinstance(column, ast.Constant) and isinstance(column.value, int):
            assert 1 <= column.value <= 79
        for keyword in node.keywords:
            if keyword.arg in ("min_column", "max_column"):
                if isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, int):
                    assert 1 <= keyword.value.value <= 79


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


def test_dashboard_geometry_and_clipping_are_explicit():
    source = TARGET.read_text(encoding="ascii")
    assert 'put(screen, 1, 1, "+" + "-" * 77 + "+"' in source
    assert 'put(screen, 13, 1, "+" + "-" * 77 + "+"' in source
    assert 'put(screen, 21, 1, "+" + "-" * 77 + "+"' in source
    assert "RADAR_LEFT, RADAR_RIGHT" in source
    assert "label_max = RADAR_RIGHT - 2" in source
    assert "label_max = RADAR_CENTER_COL + RADAR_RADIUS_X - 2" in source
    assert "selected = visible[state[\"selected\"]] if visible else None" in source
    assert 'put(screen, 2, DETAILS_LEFT + 2, "SELECTED AIRCRAFT"' in source
    assert 'put(screen, 12, detail_column, "GROUND "' in source
    assert 'put(screen, 14, 2, "CALL        ALT    SPD    HDG    RNG    AGE    ICAO    V/S"' in source
    assert 'put(screen, 0, 24, "RANGE %3d NM"' in source
    assert 'footer = "J/K SELECT | +/- ZOOM | 1-4 RANGE | L LABELS | G GROUND | H HELP | Q QUIT"' in source


def test_key_and_exit_paths_remain_present():
    source = TARGET.read_text(encoding="ascii")
    assert 'if bbs.keypressed:' in source
    assert 'key, extended = bbs.getkey()' in source
    assert 'if key == "q":' in source
    assert 'return False, False, False' in source
    assert 'while True:' in source
    assert 'time.sleep(0.05)' in source
