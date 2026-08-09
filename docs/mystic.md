# Mystic Integration

The supported integration in this repository is the standalone Mystic BBS
1.12 A48 MPY door at:

```text
integrations/mystic/standalone/ansiradar.mpy
```

## Menu Entry

Copy the file to the Mystic doors directory:

```sh
cp integrations/mystic/standalone/ansiradar.mpy \
   /home/mystic/doors/ansiradar-standalone.mpy
```

Use the following Mystic menu values:

```text
Command: GZ
Data: /home/mystic/doors/ansiradar-standalone.mpy
```

The door expects `mystic_bbs` to be supplied by Mystic's GZ Python runtime.
Do not install a wrapper, pip dependency, virtual environment, or site-package
for this door.

## Data Source

The default receiver is latitude `58.662`, longitude `6.717`, with a default
range of `100` nautical miles. The input file is:

```text
/home/mystic/doors/data/aircraft.json
```

Missing or invalid data is reported on the status line without terminating the
door.

## Real-World Verification

The following require a real Mystic 1.12 A48 BBS and an 80x25 terminal:

- door launch and display fit
- first-press key response
- normal `Q` return to the Mystic menu
- connection survival after exit
- repeated entry and exit
