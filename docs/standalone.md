# Standalone Door

The standalone door is an independent Mystic-native implementation. It does
not import, package, or reuse the ANSIRadar Python package.

## Runtime Contract

- Target: Mystic BBS 1.12 A48, Linux x86-64, Mystic GZ Python 3.
- Terminal: nominal 80x25; printable drawing area is columns 1-79 and rows
  1-24.
- Input: readsb/dump1090-style `/home/mystic/doors/data/aircraft.json`.
- Runtime dependencies: Python standard library plus `mystic_bbs`.
- Exit: normal script EOF after `Q`; no terminal reset or disconnect API.

## Controls

```text
Q       quit to Mystic
H / ?   help
J / K   next / previous aircraft
+ / =   zoom in
-      zoom out
1-4     25 / 50 / 100 / 200 nm
L       labels on/off
G       ground aircraft on/off
P       pause refresh
R       reload immediately
```

See [Mystic integration](mystic.md) for deployment and
[Architecture](architecture.md) for the data flow.
