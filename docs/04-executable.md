# 04 — The executables

Reproduce with:

```
python tools/ps2elf.py SLPS_254.50 --header --sections --segments
python tools/ps2elf.py BOOT.IRX --iopmod
python tools/leftovers.py SLPS_254.50 BOOT.IRX
```

Output: [`reports/executables.txt`](../reports/executables.txt),
[`reports/overlay-map.txt`](../reports/overlay-map.txt),
[`reports/leftovers.txt`](../reports/leftovers.txt).

---

## `SLPS_254.50`

```
type            2 (EXEC)
machine         0x0008  MIPS (EE, R5900)
flags           0x20924001
entry           0x00100008
program headers 62 at 0x34
section headers 94 at 0x137E88
load span       0x00000000 .. 0x002D88D8  (2984152 bytes)
```

1,281,336 bytes on disc expanding to just under 3 MB in memory. Sixty-two
program headers is unusual and ninety-four section headers is more so — most
retail PlayStation 2 executables are stripped to a handful of segments. This one
**kept its section table**, and the section table is a map of the game.

| Section | Address | File offset | Size |
|---|---|---|---|
| `.text` | `0x00100000` | `0x00001000` | 816,096 |
| `.vutext` | `0x001C73E0` | `0x000C83E0` | 10,032 |
| `.data` | `0x001C9B80` | `0x000CAB80` | 290,184 |
| `.rodata` | `0x00210980` | `0x00111980` | 139,776 |
| `.bss` | `0x00232C00` | — | 679,128 |
| `.scommon` / `.sbss` | `0x00232B80` | — | 20 / 0 |
| `.reginfo` | `0x001C9B10` | `0x00133BEC` | 24 |

There is **no `.comment` section** and no compiler identification string
anywhere in the file. *Tales of Symphonia*'s PlayStation 2 build carries
`MW MIPS C Compiler (2.4.1.01)`; *Tales of Destiny 2*'s carries nothing; this one
carries nothing. Absence is not an identification, so nothing is claimed from it
here — but see [06](06-decoder-lineage.md), where the shared C runtime settles
the question that a `.comment` string would otherwise have been needed for.

### The overlay map

Sixty-five of the ninety-four sections are zero-length `PROGBITS` markers whose
only content is their *address*. They are end-of-overlay symbols the linker
emitted, and sorting them by address reconstructs the game's module layout above
`.bss`, which ends at `0x002D88D8`:

| Group | Overlays | End addresses span |
|---|---:|---|
| `.mnu_*` — menus | 17 | `0x002D8F38` – `0x002EF608` |
| `.title_end`, `.ending_end`, `.namco*` | 4 | `0x002EF680` – `0x002FBBA0` |
| `.minigame1_end`, `.minigame2_end` | 2 | `0x0030E9C0` – `0x00321CA8` |
| `.battle_b001_end` … `.battle_b031_end`, `.battle_end` | 32 | `0x00358D70` – `0x00359808` |
| `.2dmap_end`, `.fld_event_ship_end`, `.fld_event_re01_end` … `re05`, `.3dfield_end` | 8 | `0x00384010` – `0x003913A0` |
| `.code_end` | 1 | `0x00391400` |

Which is the whole architecture of the game, named: seventeen separate menu
screens (`boot`, `story`, `status`, `grade`, `custom`, `tactics`, `mc`, `cook`,
`equip`, `magic`, `wcustom`, `item`, `shop`, `world`, `monster`, `sound`,
`name`), **thirty-one numbered battle overlays**, five field-event overlays
numbered `re01`–`re05` plus a `ship` one, a 2D map, a 3D field, and two
minigames.

The thirty-one battle overlays fit in 2,712 bytes of address spread, so they are
all close to the same size and swap into the same slot. Five of them —
`b008`, `b018`, `b025`, `b030`, `b031` — end at *exactly* `0x00358D70`, the
minimum, so they have identical extents. Whether those are the smallest real
overlays or placeholders that were never filled in is not answerable from the
section table alone. [→ 99](99-open-questions.md)

There is also a `.namco` section, zero length, at the boundary between the menu
overlays and the title screen.

### The vector unit overlays

Sections 75–92 are `.DVP.ovlytab`, `.DVP.ovlystrtab`, and sixteen
`.DVP.overlay..*` blobs — VU microprograms assembled by Sony's `dvp-as` and
carried as linker overlays. Their names are generated and carry the source
addresses they were cut from:

```
.DVP.overlay..0x0.6545347.20.0        .DVP.overlay..0x0.6526403.18.0
.DVP.overlay..0x0.6545363.21.0        .DVP.overlay..0x0.6526419.18.0
.DVP.overlay..0x0.6545379.18.0        ...
.DVP.overlay..unknvma.6545123.496.1   .DVP.overlay..unknvma.6526179.525.1
```

Two of them are `unknvma` — the assembler could not resolve a virtual address and
said so in the section name, and the name shipped. The numbers cluster into two
runs, 6,526,179–6,526,515 and 6,545,123–6,545,395, which is two source files
assembled in one pass.

### The index tables

The three container indexes live in `.data`:

| Table | File offset | Virtual address | Entries |
|---|---|---|---|
| `DAT.BIN` | `0x000D76B0` | `0x001D66B0` | 14,982 |
| `MOV.BIN` | `0x000E60CC` | `0x001E50CC` | 22 |
| `FLD.BIN` | `0x000E612C` | `0x001E512C` | 11 |

59,928 bytes of `.data` — one fifth of it — is the file system.
[→ 03](03-containers.md)

### SDK version stamps

The linked Sony libraries name themselves:

```
PsIIlibgraph3000   PsIIlibdma  3000   PsIIlibcdvd 3000   PsIIlibkernl3000
PsIIlibmtap 3000   PsIIlibpad  3010   PsIIlibmc   3010   PsIIlibvu0  3000
PsIIlibmpeg 3000   PsIIlibipu  3000
```

Eight libraries at 3.0.0 and two — `libpad` and `libmc` — at 3.0.1.0. The
runtime carries the full `libmpeg` and `libipu` error-string sets, which is how
the MPEG decoder's diagnostics ended up in the retail build
([→ 09](09-leftovers.md)).

---

## `BOOT.IRX`

```
{'name': 'IOPBOOT', 'version': '1.1', 'entry': 932, 'gp': 73100,
 'text': 40136, 'data': 212, 'bss': 21952}
```

A relocatable I/O-processor module with a `.rel.text` of 24,312 bytes — larger
than half its code, which is what relocatable means. It imports nine stock
libraries (`sysmem`, `intrman`, `loadcore`, `modload`, `sifcmd`, `sifman`,
`sysclib`, `thbase`, `thsemap`, `cdvdman`) and its entire string table beyond
those is four names:

```
SYSTEM.CNF   DAT.BIN   MOV.BIN   FLD.BIN
```

plus one diagnostic, `iop module no resident (0x%x)`.

That is the whole custom I/O-processor side of this game: 40 KB that knows how
to find four files and how to decompress. It contains five `4078` / `4079`
sites and a full decoder. [→ 06](06-decoder-lineage.md)

## `IOPRP300.IMG`

Nineteen stock Sony modules in a `romdir` archive, unmodified:

```
RESET  ROMDIR  EXTINFO  SYSMEM  LOADCORE  SIFCMD  SIFMAN  THREADMAN  IOMAN
MODLOAD  FILEIO  CDVDMAN  CDVDFSV  LOADFILE  TIMEMANI  ROMDRV  EESYNC
SYSCLIB  STDIO
```

Nothing of the game's is in here, and there is no `4078` anywhere in its 69,576
instruction words — which by the corpus's own rule is evidence the decoder is
absent rather than merely unfound. Its file stamp, 2004-10-14, is a month older
than everything else on the disc, because it came out of the SDK rather than out
of the build. [→ 02](02-disc-and-volume.md)
