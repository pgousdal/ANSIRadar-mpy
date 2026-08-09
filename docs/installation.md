# Installation

The door is designed for Mystic BBS 1.12 A48 on Linux x86-64 using Mystic GZ
Python 3. It requires only the standard library and `mystic_bbs` supplied by
Mystic.

## Install

From the repository root, copy the single MPY file:

```sh
cp integrations/mystic/standalone/ansiradar.mpy \
   /home/mystic/doors/ansiradar-standalone.mpy
```

Set the Mystic menu entry to:

```text
Command: GZ
Data: /home/mystic/doors/ansiradar-standalone.mpy
```

The radar reads:

```text
/home/mystic/doors/data/aircraft.json
```

The file is reloaded every two seconds. Missing files, malformed JSON, and a
missing `aircraft` array are shown as a safe status message instead of ending
the door.

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

`Q` exits by breaking the main loop and reaching normal script EOF. The door
does not reset the terminal, disconnect the session, or invoke a Mystic menu
command.

## Verification

Run the repository's static dependency check:

```sh
python3 tests/test_standalone_dependencies.py
```

The check verifies that the MPY file imports only `json`, `math`, `time`, and
`mystic_bbs`. Door entry, redraw behavior, key response, repeatability, and
connection survival require testing on a real Mystic BBS installation.
