# 02 — The disc and the volume

Reproduce with:

```
python tools/iso9660.py IMAGE.iso --pvd
python tools/iso9660.py IMAGE.iso
python tools/sector_map.py IMAGE.iso
```

Output: [`reports/iso-volume.txt`](../reports/iso-volume.txt),
[`reports/sector-map.txt`](../reports/sector-map.txt).

---

## Single layer, from the volume rather than from the file size

The image is 4,508,516,352 bytes, which is under the 4.7 GB a DVD-5 holds, so
the file size *suggests* a single layer. The file size is not evidence: an
image can be truncated, padded, or unpacked from an archive that reported
something else. The volume descriptor is evidence, and it says:

```
LBA 16     type 1    primary
  system id      PLAYSTATION
  volume id      
  volume space   2201424 sectors (4508516352 bytes)
  block size     2048
  path table     10 bytes at LBA 257 (L) / 259 (M)
  publisher      NAMCO LTD.
  application    PLAYSTATION
  created        2004111721501200$
LBA 17     type 255  terminator
```

**`volume space` is 2,201,424 sectors.** A single-layer DVD holds 2,298,496
sectors of 2,048 bytes; a dual-layer one holds roughly twice that. 2,201,424
fits inside one layer with 97,072 sectors to spare, so the disc is single
layer and the file size happens to agree because the image is exactly the
volume the disc declares — `2,201,424 × 2,048 = 4,508,516,352`, to the byte.

Three details in that descriptor are worth stopping on.

**The volume identifier is blank.** Not `TALES_OF_REBIRTH`, not
`SLPS_25450` — thirty-two spaces. Symphonia's nine CVM volumes shipped with
CRI's untouched defaults, `SAMPLE_GAME_TITLE`; this disc did not ship a
default, it shipped nothing at all. Both are the same kind of omission: the
field was never filled in and nothing checks it.

**The path table is ten bytes.** Ten bytes is one record, and one record is the
root directory. There are no subdirectories anywhere on this disc.

**The creation stamp carries a `$` offset byte**, which is decimal 36 — GMT plus
thirty-six quarter-hours, i.e. **UTC+9**, Japan. So `2004-11-17 21:50:12` is
local Tokyo time. All seven files carry the same offset, and their own stamps
run from 2004-10-14 to 2004-11-17:

| File | Stamp |
|---|---|
| `IOPRP300.IMG` | 2004-10-14 20:34:00 |
| `MOV.BIN` | 2004-11-01 10:52:59 |
| `FLD.BIN` | 2004-11-05 00:13:26 |
| `SLPS_254.50` | 2004-11-17 21:39:00 |
| `BOOT.IRX` | 2004-11-17 21:39:00 |
| `DAT.BIN` | 2004-11-17 21:48:11 |
| `SYSTEM.CNF` | 2004-11-17 21:49:43 |
| *volume* | *2004-11-17 21:50:12* |

That is a coherent mastering session and not a set of stamps normalised by a
tool: the executable and the IOP module were built in the same minute, the data
container was assembled nine minutes later, `SYSTEM.CNF` a minute after that,
and the volume closed twenty-nine seconds after `SYSTEM.CNF`. The video and the
field data are older by two and a half and by twelve days, which is what you
would expect of the two things nobody needed to rebuild at the end. The oldest
thing on the disc is Sony's IOP module bundle, a month older than everything
else, because it came out of the SDK rather than out of the build.

---

## Every sector accounted for

```
FIRST     LAST      SECTORS   WHAT
0         15        16        <system area>
16        16        1         <volume descriptor type 1>
17        17        1         <volume descriptor type 255>
257       257       1         <path table, L>
259       259       1         <path table, M>
273       273       1         SYSTEM.CNF
274       899       626       SLPS_254.50
900       1035      136       IOPRP300.IMG
1036      1067      32        BOOT.IRX
1068      847548    846481    MOV.BIN
847549    1790989   943441    DAT.BIN
1790990   2191181   400192    FLD.BIN

FIRST     LAST      SECTORS   CONTENT
18        256       239       data: 00424541303101000000000000000000
258       258       1         data: 01000501000001000000000000000000
260       272       13        data: 01000000010500010000000000000000
2191182   2201423   10242     all zero

image      2201424 sectors (4508516352 bytes)
slack      10495 sectors (0.4767% of the disc)
```

The three regions `sector_map.py` reports as unclaimed are not slack, they are a
**UDF bridge**. LBA 18, 19 and 20 hold `BEA01`, `NSR02` and `TEA01` — the ISO
13346 volume recognition sequence — LBAs 32 to 34 hold the UDF main volume
descriptor sequence (`*UDF LV Info` is legible at LBA 33), LBA 256 holds the
anchor pointer, and 260–272 the file set and root. That is the standard
ISO 9660 + UDF hybrid every PlayStation 2 DVD carries, and it is the same
arrangement Symphonia's PlayStation 2 disc used.

Subtract it and the genuine unused space is the run of zeros after the last
file: **10,242 sectors, 20,975,616 bytes, 0.4654% of the image.**

---

## Where the disc goes

From [`reports/disc-budget.txt`](../reports/disc-budget.txt), classifying each
container member by reading its own first bytes:

| | bytes | share |
|---|---:|---:|
| `MOV.BIN` / MPEG-2 program stream | 1,733,591,120 | **38.45%** |
| `DAT.BIN` / SPU-ADPCM | 1,297,725,472 | **28.78%** |
| `FLD.BIN` / field data | 737,617,760 | 16.36% |
| `DAT.BIN` / everything else | 541,554,894 | 12.01% |
| `DAT.BIN` / top-level codec blocks | 84,435,879 | 1.87% |
| `FLD.BIN` / tables | 81,975,232 | 1.82% |
| `DAT.BIN` / raw `TIM2` | 243,840 | 0.01% |
| `SLPS_254.50` + `IOPRP300.IMG` + `BOOT.IRX` + `SYSTEM.CNF` | 1,625,126 | 0.036% |
| *not claimed by any file* | *21,540,506* | *0.478%* |

**Video and voice together are 67.2% of the disc.** The executable and both
I/O-processor images together are 0.036% — a little over 1.6 MB of the four and
a half gigabytes.

---

## The layout question

Symphonia's PlayStation 2 disc left **16.12%** of itself empty, 686 MB, almost
all of it in a single interior gap, with its volumes placed at round decimal
LBAs — 4,000 and 900,000. The reading offered there was head separation between
the movies and the rest, and it was published as *Open* because nothing proved
it.

Rebirth is the sharper instrument for that question because it is nearly full.
If a 686 MB separation gap were policy, a disc with 20 MB to spare would still
show a smaller version of it. It shows none:

* the seven files are **contiguous end to end** from LBA 273 to LBA 2,191,181 —
  every file starts on the sector after the previous one ends, with no
  inter-file gap anywhere;
* the only unclaimed run is **after** the last file;
* no file starts at a round decimal LBA. The starts are 273, 274, 900, 1036,
  1068, 847549, 1790990.

So the 686 MB gap on Symphonia's disc is **not** a studio layout policy that
Rebirth also follows. Either it was specific to that title's mastering, or it
was an effect of having a spare gigabyte and no reason to compact.

What Rebirth *does* do is order the disc by access pattern, which costs nothing:
`MOV.BIN` occupies the entire inner region, sectors 1,068 to 847,548 — 38.5% of
the disc placed first and read linearly — then `DAT.BIN`, then `FLD.BIN`. The
grouping is real. The gap is not.

Both statements are measurements. Which of the two Symphonia's gap was is still
**Open**. [→ 99](99-open-questions.md)
