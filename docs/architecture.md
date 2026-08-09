# Architecture

ANSIRadar is deliberately a single-file embedded door rather than a Python
package. The runtime boundary is Mystic's `mystic_bbs` module; all other
runtime imports are Python standard library modules.

## Data Flow

```text
aircraft.json
    -> json/file handling
    -> coordinate validation and local radar mathematics
    -> range and ground filtering
    -> ASCII radar/table renderer
    -> bbs.rwrite()
```

The source file reloads the JSON snapshot every two seconds. The main loop
checks `bbs.keypressed` and sleeps briefly between iterations so controls do
not depend on a background worker.

## Runtime Boundaries

- Input: readsb/dump1090-style JSON at the configured absolute path.
- Output: conservative ANSI screen control sequences through `bbs.rwrite()`.
- Exit: `Q` breaks the loop and allows normal Python EOF to return control to
  Mystic.
- Dependencies: `json`, `math`, `time`, and Mystic's `mystic_bbs` module.

The radar algorithms and runtime behavior intentionally remain local to the
MPY file to keep deployment predictable on Mystic 1.12 A48.
