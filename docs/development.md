# Development

This is an embedded single-file project. Keep changes small and avoid adding
runtime dependencies or build infrastructure unless the target Mystic runtime
requires them.

## Local Checks

Run from the repository root:

```sh
python3 tests/test_standalone_dependencies.py
python3 -m compileall -q tests
git diff --check
```

The MPY extension is intentionally not treated as an installable Python
package. The dependency test parses it directly, which also avoids importing
`mystic_bbs` on a development workstation.

## Scope Rules

- Preserve the Mystic 1.12 A48 runtime contract.
- Keep the door within its embedded-safe dependency budget.
- Do not use the test environment as a substitute for a live BBS.
- Update documentation and the changelog for user-visible repository changes.

## Releases

Recommended GitHub Release assets are:

```text
ansiradar80
ansiradar-standalone.mpy
sample aircraft.json
release notes
```

Only assets that have actually been built or validated should be attached to a
release.
