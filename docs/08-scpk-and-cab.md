# 08 — `SCPK`, and the `.cab` that is not here

Reproduce with:

```
python tools/scpk.py IMAGE.iso --list --limit 20
python tools/scpk.py IMAGE.iso --census
python tools/scpk.py IMAGE.iso --dupes
```

Output: [`reports/scpk-census.txt`](../reports/scpk-census.txt),
[`reports/scpk-dupes.txt`](../reports/scpk-dupes.txt).

---

## The negative result first: no `MSCF` anywhere

The largest unidentified format in this corpus is the `.cab`. *Tales of
Symphonia* ships forty-five of them on each GameCube disc and fifty-three on the
PlayStation 2 one, all beginning `MSCF`, the Microsoft Cabinet signature. They
are not cabinets: the header is well formed and reuses the file entry, but the
folder declares zero data blocks and no compression while the payload is a third
of the declared length. The payload is not this codec — 13.6 MB scanned at every
offset, zero blocks — and it is not MSZIP, LZX or Quantum. It holds most of the
character art, and it carries the only per-asset timestamps on either Symphonia
release.

The hope for this session was more samples, and a decoder inside `SLPS_254.50`
that could be found from the loader side.

**A sweep of all 4,508,516,352 bytes of this image finds zero occurrences of
`MSCF`.** Not in the executable, not in either I/O-processor image, not in any
of the three containers, not in the slack. The full sweep is committed as
[`reports/magic-sweep.txt`](../reports/magic-sweep.txt), with the count printed
for every pattern including the ones that are zero.

So this disc contributes nothing to the `.cab` question except its absence — and
the absence is itself worth having. Three months after Symphonia's PlayStation 2
port, the same studio shipping the same kind of game on the same console used
none of it. Whatever the `MSCF` container was, it travelled with *Symphonia*
specifically, most plausibly out of the GameCube pipeline that title was ported
from, and not with the studio. It is not a Namco Tales Studio format. The
question moves back to [gc-talesofsymphonia-doc](https://github.com/vs-sr-dev/gc-talesofsymphonia-doc)
and stays open there.

The same sweep finds no `CVMH`, no `ROFSBLD`, no `SAMPLE_GAME_TITLE`, no
`PUBLISHER_NAME`, no `CRI ` and no `VAGp`. Every piece of middleware Symphonia's
PlayStation 2 disc carried is gone.

---

## The positive result: `SCPK` survived, unchanged

What *did* travel is the 2002 title's bundle container.

```
MEMBER              BYTES  COUNT   VER  KIND  FIRST MEMBER
DAT.BIN#10197      355468      6     1    15  03d53a05001c2e10
DAT.BIN#10198      697952     11     1     7  03d53a05001c2e10
DAT.BIN#10199      671308     10     1    15  03d53a05001c2e10
DAT.BIN#10200     1094296     26     1    15  03d53a05001c2e10
...
```

**744 `SCPK` bundles among the top-level members of `DAT.BIN`, holding
378,244,140 bytes and 9,917 members.** The layout is exactly what
[ps2-talesofdestiny2-doc](https://github.com/vs-sr-dev/ps2-talesofdestiny2-doc)
documents for 2002:

```
+0x00  char[4]  'SCPK'
+0x04  u16      version
+0x06  u16      flags / kind
+0x08  u32      count
+0x0C  u32      0            reserved
+0x10  u32[]    size[count]  member sizes in bytes
+...   members, concatenated in order with no padding
```

`tools/scpk.py`'s `parse()`, `block_head()`, `cmd_census()` and `cmd_dupes()` are
**copied from the 2002 pipeline with no edits** — the repository asserts this and
the assertion is checkable, since both files are published. Only the layer that
*finds* the bundles is new, because the index moved from `FILE.FPB` to the three
`.BIN` containers. That split was deliberate: if the format had drifted, the
copied half would have had to change.

The header fields have moved a little. 2002's bundles were version 1, kind 7.
Here:

| version, kind, reserved | bundles |
|---|---:|
| 1, 15, 0 | 737 |
| 1, 13, 0 | 6 |
| 1, 7, 0 | **1** |

Version is still 1 and the reserved word is still zero. The `kind` field has
gone from 7 to 15 for almost everything, with six at 13 and **one lone bundle
still at 7** — the 2002 value. If `kind` is a bit field, 7 is `0b0111` and 15 is
`0b1111`, so 2004 sets one more bit than 2002 did and one bundle did not get it.

Member counts run from 3 to 48, with a mode at 10.

### Every bundle has an `MFH` and a `THEIRSCE`

Decoding the compressed members and looking at their first four bytes:

```
first four bytes after decoding, top 20:
  raw:01000000       6296
  4d464800            744      MFH\0
  54484549            744      THEI...
  raw:00232323         695
  raw:03000000         388
```

**744 `MFH` chunks and 744 `THEIRSCE` chunks — exactly one of each in each of the
744 bundles**, with no bundle carrying two and none carrying none. The 2002
pipeline records `MFH` as appearing "exactly one per bundle" as well, with a `TM2@` palette at `+0x10`, and it is one of that
repository's open questions. Rebirth's `MFH` is the same shape and answers half
of it: at `+0x10` there is a **`TIM2`**, not a `TM2@`, so the chunk is a
map/texture header wrapping a standard PlayStation 2 texture:

```
4d 46 48 00 10 00 00 00 50 04 10 00 58 04 10 00   MFH.....P...X...
54 49 4d 32 04 00 01 00 00 00 00 00 00 00 00 00   TIM2............
```

`+0x04` is `0x10`, the offset of the `TIM2`; `+0x08` and `+0x0C` are two further
offsets into the same buffer.

`THEIRSCE` is an eight-byte magic that does not appear in any earlier title in
this corpus. Inside the bundles its chunks decompress to between **70 and 52,390
bytes**, median 9,560, 8,135,814 bytes in total, always exactly one per bundle,
and their header carries a length, a count and a run of small `u16` values that
look like an offset table:

```
54 48 45 49 52 53 43 45 36 00 00 00 e0 13 00 00   THEIRSCE6.......
ce 04 00 00 4a 00 00 00 24 00 26 00 28 00 30 00   ....J...$.&.(.0.
```

One per scene bundle, sized like text, alongside exactly one texture header, is
the shape of a scenario script. It is not decoded here.

There are more of them than there are bundles. Searching the raw image for the
literal bytes `THEIRSCE` returns **829 occurrences, all inside `DAT.BIN`, exactly
one per top-level member across 829 members**. 744 of those members are the
`SCPK` bundles, where the hit is the compressed chunk's own literal prefix — the
first eight plaintext bytes are emitted as literals right after the nine-byte
block header, so the magic survives compression in plain sight. The **other 85
are not bundles at all**: ordinary `DAT.BIN` members, mostly with the hit at
offset 34, carrying a `THEIRSCE` outside the bundle structure entirely. So the
disc holds 829 of these chunks and only 744 of them are where the container
puts them. [→ 99](99-open-questions.md)

---

## What a bundle costs

```
distinct bundle members 2513
bundle member instances 9917
bytes stored            378244140
bytes that are copies   175173412 (46.3%)
```

**46.3% of the bytes inside `SCPK` bundles are copies of bytes inside other
`SCPK` bundles.** 175 MB — 3.9% of the whole disc — is redundancy.

That is not waste, it is the point of the format. The 2002 documentation puts it
plainly: a bundle is the unit a scene loads, one seek and one read, everything
that scene needs including copies of things other scenes also need. On a DVD
with a 10× read speed and a seek measured in hundreds of milliseconds, paying
175 MB to avoid a second seek per scene is a good trade, and this disc had the
space — it still finished at 99.52% full.

The most-copied members show the shape of it:

| copies | each | total |
|---:|---:|---:|
| 695 | 4 | 2,780 |
| 694 | 5,176 | 3,592,144 |
| 693 | 4,168 | 2,888,424 |
| 565 | 9,300 | 5,254,500 |
| 534 | 5,232 | 2,793,888 |
| 233 | 92,032 | 21,443,456 |
| 218 | 62,760 | 13,681,680 |
| 216 | 83,712 | 18,081,792 |

Five members appear in essentially every bundle — the system font, the interface
atlas, the shared palettes — and a second tier of six appears in a third of them,
at 60–90 KB each. Twenty-one megabytes of the disc is one 92 KB asset, 233 times.
