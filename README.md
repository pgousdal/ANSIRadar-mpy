# ANSIRadar

![Python 3](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

ANSIRadar is a small aircraft-radar display project for readsb/dump1090-style
JSON data. This checkout currently provides a standalone Mystic BBS 1.12 A48
GZ Python door designed for an 80x25 terminal. It is intentionally embedded,
dependency-free, and independent of the ANSIRadar Python package.

## Key Features

- Reads `/home/mystic/doors/data/aircraft.json` directly.
- Calculates local great-circle distance and bearing without external packages.
- Displays an ASCII radar scope and nearest-aircraft table.
- Refreshes every two seconds while remaining responsive to keyboard input.
- Handles missing files, malformed JSON, and incomplete aircraft records safely.
- Returns to Mystic through normal script EOF when `Q` is pressed.

## Screenshots

Screenshots are not committed yet. Placeholder descriptions are tracked in
[`docs/screenshots/README.md`](docs/screenshots/README.md).

## Project Components

| Component | Location | Status |
| --- | --- | --- |
| Standalone Mystic door | `integrations/mystic/standalone/ansiradar.mpy` | Available |
| Native executable | Not present in this checkout | Not applicable |
| Python package | Not part of this project | Intentionally excluded |

Choose the standalone door when the target is Mystic BBS and no Python package
environment is available. It is the only implementation shipped here today.

## Quick Start

```sh
cp integrations/mystic/standalone/ansiradar.mpy \
   /home/mystic/doors/ansiradar-standalone.mpy
```

Configure the Mystic menu entry as:

```text
Command: GZ
Data: /home/mystic/doors/ansiradar-standalone.mpy
```

See [Installation](docs/installation.md) and [Mystic integration](docs/mystic.md)
for the complete setup.

## Development

Run the repository checks from its root:

```sh
python tests/test_standalone_dependencies.py
python -m pytest tests/
python -m compileall -q .
git diff --check
```

The project has no pip, virtual environment, site-packages, or build-step
requirement. See [Development](docs/development.md) for scope and validation.

## Project Status

The standalone door is implemented and statically validated. Door entry,
terminal rendering, key response, repeatability, and connection survival must
still be verified on a real Mystic BBS 1.12 A48 installation.

## License

Released under the [MIT License](LICENSE).
