# FAQ

## Is this the ANSIRadar Python package?

No. The MPY door is a separate, self-contained implementation for Mystic.

## Do I need pip or a virtual environment?

No. Mystic supplies `mystic_bbs`; the door uses only Python standard library
modules in addition to it.

## Where does aircraft data come from?

The door reads a local readsb/dump1090-style JSON snapshot. A synthetic sample
is available in [`examples/aircraft.sample.json`](../examples/aircraft.sample.json).
It is not live data.

## Why is there no native executable here?

This checkout contains the standalone Mystic MPY implementation only. Native
implementations, if maintained elsewhere, are not part of this repository.

## Has the door been tested on a live BBS?

Static parsing and dependency checks are automated. Live Mystic entry, exit,
terminal behavior, and connection survival must be verified on the target BBS.
