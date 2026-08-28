# 01 — Overview

*Tales of Rebirth*, PlayStation 2, **SLPS-25450**, published by Namco and
developed by Namco Tales Studio. Japan only; there has never been a release in
any other territory. The disc's primary volume descriptor is stamped
**2004-11-17 21:50:12**, and the game went on sale in Japan on 16 December 2004.

This repository is **documentation and analysis only**. It contains no disc
image, no extracted asset, no executable, no patch and no translation. There is
no porting, BYOA or modding intent. Every number quoted anywhere in `docs/` was
produced by running the tools in [`tools/`](../tools/) against an image supplied
separately, and the output of those runs is committed under
[`reports/`](../reports/) so that a reader who does not own the disc can still
check the arithmetic.

---

## The disc in one screen

| | |
|---|---|
| Product code | **SLPS-25450** (`SYSTEM.CNF`: `BOOT2 = cdrom0:\SLPS_254.50;1`, `VER = 1.02`, `VMODE = NTSC`) |
| Media | one **single-layer** DVD — 2,201,424 sectors, **4,508,516,352 bytes** |
| Volume | ISO 9660 plus a UDF bridge; publisher `NAMCO LTD.`, application `PLAYSTATION`, **volume identifier blank** |
| Stamped | 2004-11-17 21:50:12, GMT+9 |
| File system | **seven files, zero directories** |
| Executable | `SLPS_254.50`, 1,281,336 bytes, R5900 ELF with its **section table intact** |
| I/O processor | `IOPRP300.IMG` (nineteen stock Sony modules) and `BOOT.IRX` (`IOPBOOT` 1.1, the only custom one) |
| Containers | `MOV.BIN` 1.73 GB, `DAT.BIN` 1.93 GB, `FLD.BIN` 0.82 GB — **no headers**, indexed from the executable |
| Block codec | **yes** — Wolf Team's in-house LZSS, on **both** processors |
| Disc used | **99.52%**; 0.478% is slack, and there is no separation hole |

The whole file system is:

```
LBA         SECTORS        BYTES  PATH
273               1           57  SYSTEM.CNF
274             626      1281336  SLPS_254.50
900             136       278305  IOPRP300.IMG
1036             32        65428  BOOT.IRX
1068         846481   1733592320  MOV.BIN
847549       943441   1932165184  DAT.BIN
1790990      400192    819593216  FLD.BIN
```

That is the entire disc. There are no names for anything inside those three
containers, no directory of assets, and no middleware volume. Everything the
game loads, it loads by index number out of a table compiled into
`SLPS_254.50`. [→ 03](03-containers.md)

---

## What this disc was opened to answer

The shared corpus, [tales-blockcodec-doc](https://github.com/vs-sr-dev/tales-blockcodec-doc),
tracks one in-house LZSS from the Super Famicom in 1995 to the PlayStation 2 in
2004. Going into this session it recorded six builds across four consoles, two
dialects split 1995/1997, and one conclusion that had only just been reached:
that **somebody edited the decoder's source in 2004**, because *Tales of
Symphonia*'s PlayStation 2 port shares six bytes with *Tales of Destiny 2*'s
2002 build on the same CPU, against 212 bytes for the 1997/2000 pair.

*Tales of Rebirth* is the natural control for that. Same studio, same console,
same compilation window — Symphonia PS2 was stamped 2004-08-17 and this disc
2004-11-17, **three months apart** — so byte equality was available, and if the
2004 edit had gone into a shared source file it should still be there.

It is not, and the disc goes further than that: it proves the availability
rather than assuming it. [→ 06](06-decoder-lineage.md)

---

## Five answers

**1 — The decoder is no longer shared, and this time there is no toolchain
excuse.** The longest identical byte run between Rebirth's decoder and
Symphonia's, at any alignment anywhere in either executable, is **17 bytes**.
The corpus's own positive control — 1997's decoder against 2000's executable —
reproduces at **212 bytes** through the same tool. And the control that matters
is new: **932 bytes of Rebirth's C runtime, measured identically, matches
Symphonia for 276 contiguous bytes and Destiny 2 for 288.** The runtime is the
same object in all three games; the decoder is not the same object in any two of
them. Byte equality was on the table and the decoder did not take it.
[→ 06](06-decoder-lineage.md)

**2 — And Rebirth's decoder is a third design, not either of the other two.**
Every build from 1997 to 2003 clears the 4,096-byte dictionary with an inline
byte loop bounded by **4078**. Symphonia 2004 calls a hand-written quadword
`bzero` with **4080**. Rebirth 2004 calls the ordinary C library `memset` with
**4079** — from a *factored* `ring_init` that both method variants share, which
neither of the other two builds has. Three builds, three different ways to clear
the same array, and 4,079 is the only one that covers both cursor starts at
once. The `4080` signature the corpus called "the source fingerprint" **does not
appear anywhere in this executable**. [→ 06](06-decoder-lineage.md)

**3 — The container answer is neither of the two the corpus expected.** No
`CVM`, no `CVMH`, no `ROFSBLD`, no `SAMPLE_GAME_TITLE`: CRI's ROFS middleware,
which Symphonia used on nine volumes two months earlier, is **completely absent**
from this disc. Neither is there a `FILE.FPB`. What there is instead is three
headerless `.BIN` blobs with their index compiled into the executable using the
**exact encoding of the 2002 title's `FILE.FPB`** — 64-byte-aligned offsets with
the member's trailing padding packed into the low six bits. So Symphonia's CVMs
were an artefact of the GameCube port, and the studio's own habit is the 2002
one. [→ 03](03-containers.md)

**4 — `SCPK` survived and `MSCF` did not.** The bundle container of the 2002
title is here, 744 of them holding 378 MB, and the 2002 pipeline's parser reads
them **without a single edit**. The forty-five-per-disc `.cab` archives that are
the corpus's largest unidentified format are **not here at all**: a sweep of all
4,508,516,352 bytes of the image finds **zero occurrences of `MSCF`**. So the
`.cab` question gains no samples, and gains instead the information that the
format was not a studio-wide convention. [→ 08](08-scpk-and-cab.md)

**5 — A nearly-full disc still does not leave a separation hole.** Symphonia PS2
left 16.12% of its disc empty, 686 MB in one gap, with volumes at round decimal
LBAs; that was read as head-separation and flagged as unproven. Rebirth leaves
**0.478%**, 10,242 sectors, all of it in one run at the very end after the last
file. There is no interior hole of any size. The disc is nonetheless *ordered* —
all 1.73 GB of video first, then the data, then the field — so grouping by
access pattern is real and cost-free, while spending 686 MB on it is not
something this disc did. [→ 02](02-disc-and-volume.md)

---

## And the archaeology

The executable carries a **romanised English name table for the entire cast** —
`Lungberg`/`Veigue`, `Gallardo`/`Eugene`, `Rhambling`/`Hilda`, `Barrs`/`Annie`,
`Crowe`/`Tytree`, `Bennett`/`Claire`, `Lindblum`/`Agarte`, `Mao` — surname
first, in eight-byte slots, in a game that has never been published outside
Japan. Beside it, **thirty-eight location names in English**, from
`Cyglorg's Chambers` to `Great Pokunan Bridge`, and around a hundred battle
effect names, several misspelled (`INPACT *2`, `AUTO DEFFEND`, `REGIST UP`).

The memory-card code carries two format strings: the real one,
`BISLPS-25450ToRsv%02d`, and immediately after it **`BISLPS-00000ToRsv%02d`** —
the same string with the product code left as zeroes. There is an
`initialize debug window` next to `initialize field res data`. There is a
`fatal : '%s' is not found` whose fallback path is **`host0:`**, the devkit's
host file system, still reachable in the retail build. There is a
`[CommonEffectDraw] sc-decode buffer over!!` that names the decoder. The
movie index has **an empty slot at position 0** and the data index has **359
of them**. And the heap checker is called `ToRHeapCheckToR`.
[→ 09](09-leftovers.md)

---

## Where to go next

| | |
|---|---|
| [02 — The disc and the volume](02-disc-and-volume.md) | single layer proved from the volume, sector accounting, the layout question |
| [03 — The three containers](03-containers.md) | `.BIN`, the index in the executable, the padding-in-low-six-bits encoding, the nesting levels |
| [04 — The executables](04-executable.md) | `SLPS_254.50`, its ninety-four sections, the overlay map, the SDK stamps, the IOP modules |
| [05 — The block codec on this disc](05-block-codec.md) | the census, the packer's habits, block sizes, the stored path |
| [06 — Decoder lineage](06-decoder-lineage.md) | **the headline**: the measurement, the controls, and what it means |
| [07 — Video and audio](07-video-and-audio.md) | twenty MPEG-2 movies, 1.30 GB of SPU-ADPCM |
| [08 — SCPK, and the `.cab` that is not here](08-scpk-and-cab.md) | continuity with 2002, and a negative result |
| [09 — Leftovers](09-leftovers.md) | the archaeology, in full |
| [99 — Open questions](99-open-questions.md) | what is still unresolved, with the measurement beside it |
