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
    assert values["RADAR_PANEL_LEFT"] == 2
    assert values["RADAR_PANEL_RIGHT"] == 39
    assert values["RADAR_PANEL_TOP"] == 3
    assert values["RADAR_PANEL_BOTTOM"] == 14
    assert values["DETAILS_LEFT"] == 41
    assert values["RADAR_DIVIDER"] == 40
    assert values["RADAR_RING_COUNT"] == 4
    assert values["RADAR_RING_SAMPLES"] == 12
    assert values["RADAR_PANEL_RIGHT"] - values["RADAR_PANEL_LEFT"] + 1 == 38
    assert values["RADAR_PANEL_BOTTOM"] - values["RADAR_PANEL_TOP"] + 1 == 12


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
    assert "RADAR_PANEL_WIDTH = RADAR_PANEL_RIGHT - RADAR_PANEL_LEFT + 1" in source
    assert "RADAR_PANEL_HEIGHT = RADAR_PANEL_BOTTOM - RADAR_PANEL_TOP + 1" in source
    assert "RADAR_CENTER_X = RADAR_PANEL_LEFT + RADAR_PANEL_WIDTH / 2.0" in source
    assert "RADAR_CENTER_Y = RADAR_PANEL_TOP + (RADAR_PANEL_HEIGHT - 1) / 2.0" in source
    assert "RADAR_RADIUS_X = RADAR_PANEL_WIDTH / 2.0 - 2.0" in source
    assert "RADAR_RADIUS_Y = (RADAR_PANEL_HEIGHT - 1) / 2.0" in source
    assert "radar_put(screen, ring_row, ring_column" in source
    assert "for ring_number in range(1, RADAR_RING_COUNT + 1)" in source
    assert "ring_bearing = 360.0 * ring_sample / RADAR_RING_SAMPLES" in source
    assert "label_max = RADAR_PANEL_RIGHT - 1" in source
    assert "RADAR_CENTER_COL" not in source
    assert "RADAR_CENTER_SCREEN_ROW" not in source
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
