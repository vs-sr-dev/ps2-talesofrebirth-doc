# 05 — The block codec on this disc

Reproduce with:

```
python tools/tales_block.py --selftest
python tools/codec_census.py IMAGE.iso --nested
python tools/scpk.py IMAGE.iso --census
```

Output: [`reports/selftest.txt`](../reports/selftest.txt),
[`reports/codec-census.txt`](../reports/codec-census.txt),
[`reports/codec-totals.txt`](../reports/codec-totals.txt),
[`reports/scpk-census.txt`](../reports/scpk-census.txt).

The format itself is not restated here. It is specified once, for all titles, in
[tales-blockcodec-doc](https://github.com/vs-sr-dev/tales-blockcodec-doc). This
document is only what *this* disc does with it.

---

## No new dialect

`tools/tales_block.py` is byte-identical to the corpus's reference decoder —
same SHA-1, copied rather than adapted, which is the whole point of the exercise.
Run against every block on the disc, at all three levels of nesting:

```
=== WHOLE DISC
    method 1 lzss                    711  (24.9%)
    method 3 lzss + run escape      2140  (75.1%)
    decode to declared length      2851 of 2851
    packed / unpacked / ratio      284853597 / 1061471968 / 3.726x
    largest packed block           1015400  (DAT.BIN#21)
    smallest packed block          59  (DAT.BIN#10198[10])
    blocks that did not shrink     0
```

**2,851 of 2,851.** No Rebirth branch, no nibble swap, no dictionary variant, no
header byte-order question. Two dialects, seven builds, four consoles, both byte
orders, nine years, and the split is still 1995/1997.

Split by where the blocks live:

| Level | Blocks | Method 1 | Method 3 | Packed | Unpacked | Ratio |
|---|---:|---:|---:|---:|---:|---:|
| Top level, container index | 1,312 | 85 (6.5%) | 1,227 (93.5%) | 83,063,497 | 255,251,086 | 3.073× |
| Inside `SCPK` bundles | 1,488 | 624 (41.9%) | 864 (58.1%) | 201,691,293 | 805,899,102 | **3.996×** |
| Inside `.BIN` bundles | 51 | 2 (3.9%) | 49 (96.1%) | 98,807 | 321,780 | 3.257× |
| **Total** | **2,851** | **711** | **2,140** | **284,853,597** | **1,061,471,968** | **3.726×** |

A gigabyte of data comes off 285 MB of disc. That is the largest compressed
corpus in this project by a factor of two, and it is still only 6.3% of the
image — the rest is video and voice, neither of which goes through this codec.

---

## What the packer did here

The corpus's standing open question is *what produced the blocks*. The packer
has never been found in a shipped image; all that can be measured is its habits.
This disc adds a third measurement point inside the 2002–2004 window and it
moves two of the habits and confirms one.

### The stored path is gone

| Title | Year | Blocks | Method 0 |
|---|---|---:|---:|
| Tales of Destiny | 1997 | 6,638 | **0** |
| Tales of Eternia | 2000 | 21,054 | 969 |
| Tales of Destiny 2 | 2002 | 9,469 | 21 |
| Tales of Symphonia GC | 2003 | 487 | 0 |
| **Tales of Rebirth** | **2004** | **2,851** | **0** |

Not one stored block anywhere on this disc. The 2000 packer wrapped tiny
incompressible payloads — 16, 24 and 28 bytes — in a method-0 header; the 2002
one had almost stopped, emitting 21, and left tiny members raw with no header at
all instead. Rebirth completes that move. Its **smallest block is 59 packed
bytes and it is a method-1 LZSS block**, not a stored one, so the packer is now
compressing payloads that earlier versions of it would have declined to touch.
And nothing on the disc expanded: **zero of 2,851 blocks have packed ≥
unpacked.**

### The thirty-fold ceiling holds

Up to and including 2002 the largest block in any title was around 30 KB. The
2003 GameCube build broke that by a factor of thirty — 1,007,213 packed bytes in
one block — and the corpus recorded it as unexplained.

Rebirth's largest is **1,015,400 packed bytes**, in `DAT.BIN` member 21. So
whatever changed between 2002 and 2003 was not a GameCube-specific decision and
did not revert: eighteen months later, on a different console and a different
title, the packer is still willing to emit a one-megabyte block. The
twenty-four-bit size field always allowed it. Something about the tool changed
in 2003 and stayed changed.

### The per-archive setting is per-archive again

The corpus notes that the run escape is not a global switch: on the 2000 disc
two archives were packed with it and two without, and on the 2002 disc method 3
was 98.7% of blocks nested inside bundles but only a minority at the top level.

Rebirth does the same thing, in the same direction, with a sharper contrast:

* top-level members: **93.5% method 3**
* inside `SCPK` bundles: **58.1% method 3**

Same disc, same packer, same day, two populations that disagree by thirty-five
points. The dispatcher does not care which is used, so nothing ever forced the
settings to agree, and evidently nobody made them.

### Compression is better where the data is more repetitive

The `SCPK` level reaches **3.996×** against 3.073× for the top level. That is a
property of the corpus rather than the codec — `SCPK` bundles are scene loads,
and 46.3% of their bytes are copies of bytes in other bundles
([→ 08](08-scpk-and-cab.md)) — but it is worth recording next to the corpus's
warning that ratios measure corpora and not codecs. Here both numbers come from
one disc and one packer run, so the difference really is the data.

---

## Where the blocks are

Nothing here was found by scanning. Every block above sits at an offset some
index declares, which is what makes "2,851 of 2,851" a measurement rather than a
survivor count from a filter.

`codec_census.py --scan` does the opposite job and is reported honestly: swept
the whole of `DAT.BIN`, 1,932,165,184 bytes, at 64-byte steps in **177.5
seconds**, nothing abandoned, and found **1,068 offsets that decode to their own
declared length and are not top-level index entries**. (An earlier run of the
same sweep returned 1,186. It was wrong twice over — its chunk overlap was
smaller than the largest block on the disc, so it missed some, and it rescanned
the overlap without de-duplicating, so it counted others twice. Both are fixed
in the committed tool and both are commented in it.) Those are not orphans —
they are the blocks inside `SCPK` bundles and inside `.BIN` bundles, seen from
outside their containers. The scan finds only the subset that happens to land on
a 64-byte boundary; `SCPK` concatenates its members with no padding, so most of
its 1,488 do not, which is why the container walk finds more than the sweep does.

The top-level index leaves nothing to find. Member sizes plus declared padding
equal each container's length exactly — 1,932,057,780 + 107,404 = 1,932,165,184
for `DAT.BIN` — so no unclaimed region larger than 63 bytes exists anywhere in
any of the three. [→ 03](03-containers.md)

---

## The decoder that reads them

Two copies, one per processor, both with the `4078` / `4079` cursors, both
dispatching on internal kinds 2 and 4 rather than the on-disc method bytes, and
neither sharing meaningful code with any other build in the corpus.
[→ 06](06-decoder-lineage.md)
