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
    assert values["__version__"] == "0.1.0"
    assert values["SCREEN_WIDTH"] == 79
    assert values["SCREEN_HEIGHT"] == 24
    assert values["RADAR_RING_COUNT"] == 4
    assert values["RADAR_RING_SAMPLES"] == 72

    left = values["RADAR_PANEL_LEFT"]
    right = values["RADAR_PANEL_RIGHT"]
    top = values["RADAR_PANEL_TOP"]
    bottom = values["RADAR_PANEL_BOTTOM"]
    assert 1 <= left < right <= values["SCREEN_WIDTH"]
    assert 1 <= top < bottom <= values["SCREEN_HEIGHT"]
    assert values["RADAR_DIVIDER"] == right + 1
    assert values["DETAILS_LEFT"] == values["RADAR_DIVIDER"] + 1


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
    assert "# SPDX-License-Identifier: MIT" in source
    assert "# Copyright (c) 2026 ANSIRadar contributors" in source
    assert "[list(\" \" * SCREEN_WIDTH) for unused in range(SCREEN_HEIGHT)]" in source
    assert "screen_output(screen, colours)" in source
    assert "output += screen_output(screen, colours)" in source
    assert "ESC + \"2J\" + ESC + \"H\"" in source
    assert "ESC + \"c\"" not in source


def test_dashboard_geometry_and_clipping_are_explicit():
    source = TARGET.read_text(encoding="ascii")
    assert 'put(screen, 1, 1, "+" + "-" * 77 + "+"' in source
    assert 'put(screen, 15, 1, "+" + "-" * 77 + "+"' in source
    assert 'put(screen, 21, 1, "+" + "-" * 77 + "+"' in source
    assert "RADAR_PANEL_WIDTH = RADAR_PANEL_RIGHT - RADAR_PANEL_LEFT + 1" in source
    assert "RADAR_PANEL_HEIGHT = RADAR_PANEL_BOTTOM - RADAR_PANEL_TOP + 1" in source
    assert "RADAR_CENTER_X = RADAR_PANEL_LEFT + RADAR_PANEL_WIDTH / 2.0" in source
    assert "RADAR_CENTER_Y = RADAR_PANEL_TOP + (RADAR_PANEL_HEIGHT - 1) / 2.0" in source
    assert "RADAR_RADIUS_X = RADAR_PANEL_WIDTH / 2.0 - 0.75" in source
    assert "RADAR_RADIUS_Y = (RADAR_PANEL_HEIGHT - 1) / 2.0 - 0.35" in source
    assert "radar_put(screen, ring_row, ring_column" in source
    assert "for ring_number in range(1, RADAR_RING_COUNT + 1)" in source
    assert "ring_bearing = 360.0 * ring_sample / RADAR_RING_SAMPLES" in source
    assert "RADAR_PANEL_LEFT + 1" in source
    assert "RADAR_PANEL_RIGHT - 1" in source
    assert "RADAR_CENTER_COL" not in source
    assert "RADAR_CENTER_SCREEN_ROW" not in source
    assert "selected = visible[state[\"selected\"]] if visible else None" in source
    assert 'put(screen, 2, detail_col, "SELECTED"' in source
    assert 'put(screen, row - 1, detail_col, label' in source
    assert '"CALL        ALT     SPD    HDG    RNG   AGE   ICAO    V/S"' in source
    assert 'put(screen, 0, 23, "RANGE %3d NM"' in source
    assert '"J/K SELECT | +/- ZOOM | 1-4 RANGE | L LABELS | "' in source
    assert '"G GROUND | H HELP | Q QUIT"' in source


def test_dashboard_rows_are_non_overlapping_and_fit_screen():
    values = constants()
    table_header_row = 17
    table_last_row = 20
    status_row = 21
    footer_row = 23

    assert values["RADAR_PANEL_BOTTOM"] < table_header_row
    assert table_last_row < status_row < footer_row <= values["SCREEN_HEIGHT"]
    assert values["DETAILS_LEFT"] <= values["SCREEN_WIDTH"]
    assert values["RADAR_PANEL_RIGHT"] < values["RADAR_DIVIDER"] < values["DETAILS_LEFT"]


def test_table_window_helper_is_present_and_uses_selected_index():
    source = TARGET.read_text(encoding="ascii")
    assert "def table_window(items, selected_index, max_rows):" in source
    assert "table_items, table_start = table_window(visible, state[\"selected\"], 3)" in source
    assert "aircraft_index = table_start + row_offset" in source


def test_key_and_exit_paths_remain_present():
    source = TARGET.read_text(encoding="ascii")
    assert 'if bbs.keypressed:' in source
    assert 'key, extended = bbs.getkey()' in source
    assert 'if key == "q":' in source
    assert 'return False, False, False' in source
    assert 'while True:' in source
    assert 'time.sleep(0.05)' in source
