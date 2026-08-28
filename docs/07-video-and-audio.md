# 07 — Video and audio

Reproduce with:

```
python tools/mpeg.py IMAGE.iso
python tools/binfs.py IMAGE.iso --census
```

Output: [`reports/movies.txt`](../reports/movies.txt),
[`reports/bin-census.txt`](../reports/bin-census.txt),
[`reports/disc-budget.txt`](../reports/disc-budget.txt).

Together these are **67.2% of the disc**, which is the single largest fact about
how this DVD was spent.

---

## Video: `MOV.BIN`

Twenty MPEG-2 program streams laid end to end, 1,733,591,120 bytes, plus one
empty slot at index 0.

Nothing announces where one movie ends. `MOV.BIN` has no header and no table of
contents; the boundaries come from the twenty-two-entry index in `SLPS_254.50`
([→ 03](03-containers.md)), and the check that the index is right is that
**every declared offset lands exactly on a `00 00 01 BA` pack header.** All
twenty do.

Every one of them is encoded identically:

| | |
|---|---|
| Picture | **640 × 448** |
| Aspect ratio code | 2 — 4:3 |
| Frame rate code | 4 — **29.97 fps** |
| Bit rate | **9,000,000 bit/s**, constant, declared in the sequence header |
| Muxed duration | 1,541 seconds total — **25.7 minutes** |

640 × 448 is the PlayStation 2's usual full-frame NTSC video size, and 9 Mbit/s
is a high but ordinary setting for the era; the console's IPU decodes it in
hardware, which is why `libipu` and `libmpeg` are linked into the executable.

The sizes are very uneven:

| Movie | Bytes | Muxed seconds |
|---:|---:|---:|
| 14 | 358,367,236 | 318.5 |
| 19 | 311,132,164 | 276.6 |
| 18 | 289,570,820 | 257.4 |
| 20 | 263,634,948 | 234.3 |
| 1 | 143,245,316 | 127.3 |
| … | … | … |
| 7 | 7,929,860 | 7.0 |

Four of the twenty account for **71%** of the video, and each runs four to five
minutes. At a fixed 9 Mbit/s with no per-scene reset, those are almost certainly
reels — several cut scenes muxed into one stream and seeked into — rather than
single five-minute sequences. The four shortest run seven to fifteen seconds
each, which is the length of a transition.

Slot 0 is an index entry of length zero. It is not padding — it is an entry in a
table of twenty-one, pointing at offset 0 with size 0, ahead of the first real
movie. [→ 09](09-leftovers.md)

---

## Audio: 1.30 GB of raw SPU-ADPCM in `DAT.BIN`

There is no `.adx`, no `.afs`, no `VAGp` header and no CRI audio middleware
anywhere on this disc — a sweep of all 4,508,516,352 bytes finds **zero**
occurrences of `VAGp`. What there is instead is 11,036 members of `DAT.BIN`,
totalling **1,297,725,472 bytes**, which are headerless PlayStation 2 SPU ADPCM
sample banks — the format the sound processor's DMA reads directly, with nothing
wrapped round it.

That is 28.78% of the disc, and it is more than a quarter of the DVD spent on
voice.

### How they were identified

Not by a magic number, because they do not have one. An SPU-ADPCM frame is
sixteen bytes: a shift/filter byte whose low nibble is a shift of at most 12 and
whose high nibble is a filter of at most 4, a flag byte of at most 7, then
fourteen bytes of packed nibbles. `binfs.py` classifies a member as SPU-ADPCM
only if it opens with the all-zero silent frame these banks always begin with
**and** every frame header in its first 4 KB is legal. Applied to the 11,148
members that begin with four zero bytes, that test accepts **11,036** and
rejects 112, and the 112 rejects are visibly something else. A test that
accepted everything it was pointed at would not be worth running.

The flag bytes confirm the reading. A representative member's histogram is

```
flag 0 x3    flag 2 x7687    flag 3 x3    flag 6 x3
```

which is three sample-bank entries — flag 6 to start a loop region, flag 2 for
the body, flag 3 to end one — inside one member. So a member is a *bank* of
several samples, not a single sound, and 11,036 members hold considerably more
than 11,036 recordings.

### What that says about the disc

`DAT.BIN` also carries the executable's own debug counters:

```
picture total : %d
adpcm total : %d
```

which is the loader printing how many of each it has resident. The two words
the game uses for its own content are *picture* and *adpcm*, and the disc bears
that out: pictures and ADPCM are what `DAT.BIN` is, in a ratio of about one to
four by volume.

There is no separate music container, no Red Book audio track — the disc has a
single data track — and no streaming-audio middleware. Whatever the score is
playing back through, it is playing back through the same SPU banks.
[→ 99](99-open-questions.md)
