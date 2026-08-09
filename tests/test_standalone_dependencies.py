"""Static import check for the embedded standalone Mystic door."""

import ast
from pathlib import Path

TARGET = Path(__file__).parents[1] / "integrations/mystic/standalone/ansiradar.mpy"
FORBIDDEN = {
    "ansiradar",
    "httpx",
    "httpcore",
    "anyio",
    "requests",
    "asyncio",
    "threading",
    "socket",
    "subprocess",
}
ALLOWED = {"json", "math", "time", "mystic_bbs"}


def test_standalone_dependencies():
    tree = ast.parse(TARGET.read_text(), filename=str(TARGET))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module.split(".")[0])
    unexpected = sorted(set(imports) - ALLOWED)
    forbidden = sorted(set(imports).intersection(FORBIDDEN))
    assert not forbidden, "forbidden imports: " + ", ".join(forbidden)
    assert not unexpected, "unexpected imports: " + ", ".join(unexpected)


def main():
    test_standalone_dependencies()
    print("standalone dependency check passed")


if __name__ == "__main__":
    main()
