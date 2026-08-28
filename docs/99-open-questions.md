# 99 — Open questions

Everything here is unresolved, with the measurement that bounds it beside it. A
question with a number attached is worth more than a plausible answer without
one, and nothing in the other documents has been softened to avoid landing in
this one.

---

## 1. What is `THEIRSCE`?

**Measured.** An eight-byte magic on a chunk that appears **exactly once in each
of the 744 `SCPK` bundles**, always as a compressed member, decompressing to
between 70 and 52,390 bytes — median 9,560, 8,135,814 in total. A raw search of
the image finds **829** occurrences of the literal magic, one per top-level
`DAT.BIN` member across 829 members: the 744 bundle hits are the compressed
chunk's own literal prefix, and **85 more sit in members that are not bundles at
all**. Its header is

```
54 48 45 49 52 53 43 45  36 00 00 00  e0 13 00 00
ce 04 00 00  4a 00 00 00  24 00 26 00 28 00 30 00
```

— magic, then what look like a count, two lengths, an entry count, and then a
run of ascending `u16` values on a two-byte stride that behaves like an offset
table.

**Unresolved.** What the offsets point at, and why 85 of them live outside the
bundle structure. One-per-bundle, text-sized, and paired with exactly one texture
header per bundle is the shape of a scenario script, and the name supports it,
but nothing here decodes the payload. It does
not appear in any earlier title in this corpus — 1995, 1997, 2000, 2002 and 2003
have no `THEIRSCE` — so it is either new for this title or new since 2002.

**Why it matters.** It is the only per-bundle chunk on the disc whose purpose is
unknown, and it is 744 samples of one format with a known container around it,
which is the easiest starting position any unidentified format in this corpus has
had.

---

## 2. What is inside `MFH`, still

**Measured.** 744 chunks, one per bundle, decompressing to 1,060,380 bytes each
in the sampled cases, with a `TIM2` texture at offset `0x10` and two further
`u32` offsets in the header at `+0x08` and `+0x0C`.

**Partly answered.** ps2-talesofdestiny2-doc lists `MFH` as an open question,
noting a `TM2@` palette at `+0x10` and "what the other 263 KB is". On this disc
the thing at `+0x10` is a full standard `TIM2`, not a bare palette, which
identifies the chunk as a texture wrapper rather than a palette table.

**Unresolved.** The remaining megabyte after the `TIM2`, and what the two other
header offsets reach.

---

## 3. `FLD.BIN`'s three pairs

**Measured.** Six of `FLD.BIN`'s ten members form three pairs of **identical
size and different content**:

| pair | bytes each | SHA-1 prefixes |
|---|---:|---|
| 4 / 5 | 13,565,136 | `0c376751…` / `c1e32703…` |
| 6 / 7 | 13,501,424 | `dd1a08fb…` / `4a91bba4…` |
| 8 / 9 | 13,921,056 | `ffd6e5fd…` / `fd96b9fe…` |

Each of the six opens with the same 176-byte-strided `u32` offset table, so they
share a layout exactly and share no data. The other three members are 244, 243
and 251 MB and all open with the same 36 zero bytes followed by the same
IEEE-754 float pattern.

**Unresolved.** Why a 819 MB container is exactly ten things, and why three of
its six table members come in same-size pairs. Two field data sets at identical
resolution, two lighting or collision variants, or two halves of the world are
all consistent with the measurement and none is supported by it.

---

## 4. Did Symphonia's 686 MB gap mean anything?

**Measured.** *Tales of Symphonia* PS2 (August 2004) left **16.12%** of its disc
unused, 686 MB, almost all in one interior gap, with volumes at LBA 4,000 and
900,000. *Tales of Rebirth* (November 2004), same studio, same console, leaves
**0.478%**, entirely after the last file, with all seven files contiguous end to
end and no file at a round LBA.

**What this settles.** The interior gap is not a studio layout convention. Two
discs three months apart, one with it and one without.

**Unresolved.** Whether it was head-separation for that title specifically or
simply the shape of a disc with a spare gigabyte and no reason to compact.
Rebirth cannot answer that, because Rebirth had no spare gigabyte. What Rebirth
does show is that *ordering* by access pattern survives a full disc — 1.73 GB of
video occupies the entire inner region — while *padding* does not.

---

## 5. Where did the packer's block-size ceiling come from?

**Measured.** The largest block in any title up to and including 2002 is around
30 KB. The 2003 GameCube build's largest is 1,007,213 packed bytes. This disc's
largest is **1,015,400**, in `DAT.BIN` member 21.

**What this settles.** The thirty-fold increase was not a GameCube decision and
did not revert. It is present eighteen months later on a different console and a
different title.

**Unresolved.** What changed in the tool between 2002 and 2003. The
twenty-four-bit size field always permitted it, so nothing forced the old
ceiling, and nothing in any shipped image explains why it lifted.

---

## 6. The packer is still invisible, and now it is the only thing that did not fork

**Measured.** Three PlayStation 2 builds inside thirty months clear the same
4,096-byte dictionary three different ways with three different constants —
inline `4078` (2002), a bespoke quadword `bzero` with `4080` (Symphonia 2004), a
library `memset` with `4079` from a factored `ring_init` (Rebirth 2004) — while
the on-disc format is bit-identical across all three and `tales_block.py` decodes
**2,851 of 2,851** blocks here without an edit.

**Unresolved, and reframed.** The corpus's standing question is *what produced
the blocks*. It now has a sharper edge: the decoders demonstrably diverged
per-title, and the format did not. Something was still normalising the output
across titles that were no longer sharing decoder source. Either the packer was a
single shared tool everyone ran, or the format was frozen by the data rather than
by the code. The packer itself has left no trace in any shipped image in nine
years and seven builds.

**New habits recorded here.** Zero stored blocks anywhere on the disc, against 21
in 2002 and 969 in 2000; a smallest block of 59 packed bytes that is method 1
rather than method 0; zero of 2,851 blocks that failed to shrink; and a run-escape
share that differs by thirty-five points between two populations on the same disc
(93.5% at top level, 58.1% inside `SCPK`).

---

## 7. What the `.cab` was

**Measured.** Zero occurrences of `MSCF` in all 4,508,516,352 bytes of this
image.

**What this settles.** The format was not a Namco Tales Studio convention. Three
months after Symphonia's PlayStation 2 port, the same studio on the same console
used none of it — nor any of the CRI middleware that shipped alongside it.

**Unresolved, and moved.** The question belongs to
[gc-talesofsymphonia-doc](https://github.com/vs-sr-dev/gc-talesofsymphonia-doc)
and to the GameCube pipeline that title was ported from. This disc removes one
hypothesis and supplies no samples.

---

## 8. `MINI GAME 3`

**Measured.** The string `MINI GAME 3` at `0x00111B10`, immediately after the
cast name table. The section table names exactly two minigame overlays,
`.minigame1_end` and `.minigame2_end`. There is no `.minigame3_end`.

**Unresolved.** Whether a third minigame was cut, or whether the string is a
label in a menu that numbers from something other than one.

---

## 9. Five battle overlays with identical extents

**Measured.** `.battle_b008_end`, `.battle_b018_end`, `.battle_b025_end`,
`.battle_b030_end` and `.battle_b031_end` all end at `0x00358D70` — the minimum
of the thirty-two markers. The full spread across all thirty-two is 2,712 bytes.

**Unresolved.** Same end address means same extent, which is consistent with
five stub overlays and equally consistent with five small real ones. The section
table records extents, not contents, and the contents live in `DAT.BIN` under
index numbers nothing on the disc maps to overlay names.

---

## 10. `CHT99X27`–`CHT99X99`

**Measured.** Seventy-three identifiers, contiguous and descending, on a 16-byte
stride at `0x00112EA2`. The only `CHT`-prefixed identifiers in the executable —
no group 1 through 98 exists anywhere.

**Unresolved.** A table numbered 27 to 99 inside a group numbered 99, with no
other group present, does not look like production content, and the word before
it is `notice`. What it drives is unknown.

---

## 11. The 359 empty slots

**Measured.** 359 zero-length entries in the 14,981-member `DAT.BIN` index, plus
one each at slot 0 of `MOV.BIN` and `FLD.BIN`.

**Unresolved.** Reserved and never filled, or filled and later emptied. The
containers are tiled exactly by the index — member bytes plus declared padding
equal each file's length to the byte — so an emptied slot left no gap behind, and
there is nothing on the disc to recover.

---

## 12. What plays the music

**Measured.** 1,297,725,472 bytes of raw SPU-ADPCM in 11,036 members of
`DAT.BIN`, and nothing else audio-shaped: no `VAGp`, no `.adx`, no `.afs`, no CRI
audio middleware, no second track on the disc.

**Unresolved.** Whether the score is streamed out of those same banks, sequenced
against them, or both. The flag histograms show loop regions inside members,
which is consistent with either.

---

## Answered by this disc, and closed

* **Does the 2004 decoder edit persist into the next title?** No. Seventeen
  bytes against a 276-byte C-runtime control from the same pair of files.
  [→ 06](06-decoder-lineage.md)
* **Is byte equality genuinely available between these builds?** Yes, and it is
  now demonstrated rather than assumed: 276 and 288 contiguous identical bytes
  of C runtime across the three PlayStation 2 titles. [→ 06](06-decoder-lineage.md)
* **Were Symphonia's CVMs a studio choice?** No. No CRI middleware of any kind
  on this disc. [→ 03](03-containers.md)
* **Did `FILE.FPB`'s index encoding survive?** Yes, exactly — 64-byte-aligned
  offsets with padding in the low six bits. [→ 03](03-containers.md)
* **Did `SCPK` survive?** Yes, 744 of them, parsed by the 2002 tool unchanged.
  [→ 08](08-scpk-and-cab.md)
* **Is there a third dialect?** No, for the seventh build. 2,851 of 2,851.
  [→ 05](05-block-codec.md)
* **Does the disc carry another title's data?** No, for the first time in three
  discs. [→ 09](09-leftovers.md)
