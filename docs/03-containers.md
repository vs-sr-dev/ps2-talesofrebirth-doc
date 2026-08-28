# 03 — The three containers

Reproduce with:

```
python tools/binfs.py IMAGE.iso --tables
python tools/binfs.py IMAGE.iso --census
python tools/binfs.py IMAGE.iso --list DAT.BIN --limit 40
```

Output: [`reports/bin-tables.txt`](../reports/bin-tables.txt),
[`reports/bin-census.txt`](../reports/bin-census.txt).

---

## Not CVM, and not FILE.FPB either

Going into this disc the corpus had two competing expectations. *Tales of
Destiny 2* (2002) shipped `FILE.FPB`: no header, no names, the directory
compiled into the executable, and the padding of each member packed into the low
six bits of its offset. *Tales of Symphonia* (2004) shipped nine CRI `CVM`
volumes: a `CVMH` header wrapping a real ISO 9660 file system, built by
`ROFSBLD Ver.1.52 2003-06-09`, with the builder's defaults left in place. The
question was which of those the studio would use three months after Symphonia.

The answer is that **neither of the two labels applies, and the 2002 mechanism
is what actually survived.**

A sweep of every one of the 4,508,516,352 bytes of the image finds **zero**
occurrences of `CVMH`'s magic in a header position, zero of `ROFSBLD`, zero of
`SAMPLE_GAME_TITLE`, zero of `PUBLISHER_NAME`, and no `CRI ` string anywhere.
CRI's file-system middleware is not on this disc. There is also no file called
`FILE.FPB`.

What there is:

```
CONTAINER  INDEX@FILE    ENTRIES      MEMBERS  SENTINEL
MOV.BIN    0x000E60CC         22           21  1733592320 == MOV.BIN size
DAT.BIN    0x000D76B0      14982        14981  1932165184 == DAT.BIN size
FLD.BIN    0x000E612C         11           10  819593216 == FLD.BIN size
```

Three files with no header, no magic number, no member count and no name table,
and three flat `u32` arrays inside `SLPS_254.50` that say where everything is.
That is `FILE.FPB`'s design under a different file name — including the part
nobody would reinvent by accident.

---

## The index encoding

Each entry is one little-endian `u32`:

```
entry = (64-byte-aligned offset) | (trailing padding in the low six bits)
```

so for member *i*:

```
start(i) = entry[i] & ~0x3F
size(i)  = start(i+1) - start(i) - (entry[i] & 0x3F)
```

and the last entry of each table is a sentinel equal to the container's own
length. This is the same trick, on the same bit positions, that
[ps2-talesofdestiny2-doc](https://github.com/vs-sr-dev/ps2-talesofdestiny2-doc)
documents for `FILE.FPB` in 2002.

It is worth showing the first member closing exactly, because the encoding is
the sort of thing that can be fitted to data rather than read out of it. Entry 0
of the `DAT.BIN` table is `0x00000013` — decimal 19 — and entry 1 is
`0x00001F80`:

* `start(0) = 0x13 & ~0x3F = 0`
* `pad(0) = 0x13 & 0x3F = 19`
* `size(0) = 0x1F80 - 0 - 19 = 8,045`

and the block at `DAT.BIN` offset 0 has a nine-byte header declaring a packed
length of 8,036. `9 + 8,036 = 8,045`. The nineteen bytes are the gap between the
end of that block and the next 64-byte boundary, which is where member 1 starts.

Member 1 is a raw `TIM2` texture whose own picture header declares 99,376 bytes
of data. Entry 2 is `0x0001A3F6`, so `start(2) = 0x1A3C0` and
`size(1) = 0x1A3C0 - 0x1F80 - 0 = 99,392 = 99,376 + 16`, the sixteen being the
`TIM2` file header. Two members, two independent internal length declarations,
both closed by the encoding to the byte.

### The index tiles the containers completely

There is no need to sweep for unreachable regions, because the arithmetic
settles it:

| | member bytes | index padding | sum | file size |
|---|---:|---:|---:|---:|
| `MOV.BIN` | 1,733,591,120 | 1,200 | 1,733,592,320 | 1,733,592,320 |
| `DAT.BIN` | 1,932,057,780 | 107,404 | 1,932,165,184 | 1,932,165,184 |
| `FLD.BIN` | 819,592,992 | 224 | 819,593,216 | 819,593,216 |

Every byte of all three containers is either inside a declared member or inside
a declared sub-64-byte pad. **Nothing on this disc is orphaned at the top
level**, and no region big enough to hold a superseded asset exists outside the
index. That is a stronger statement than a scan could produce, and it costs one
addition.

`binfs.py` finds all three tables without being told where they are: it searches
the executable for a word equal to the container's length in the ISO, then walks
backwards while the base offsets are non-decreasing. Nothing in the tool is
hard-coded to an address.

---

## What the members are

Classified by reading each member's own first bytes — never by position:

```
=== MOV.BIN  21 members, 1733591120 bytes
    MPEG-PS             20 members     1733591120 bytes
    empty                1 members              0 bytes

=== DAT.BIN  14981 members, 1932057780 bytes
    SPU-ADPCM        11036 members     1297725472 bytes
    raw               2160 members      541554894 bytes
    block:3           1227 members       83912537 bytes
    empty              359 members              0 bytes
    zero-lead          112 members        8097695 bytes
    block:1             85 members         523342 bytes
    TIM2                 2 members         243840 bytes

=== FLD.BIN  10 members, 819592992 bytes
    raw                  6 members       81975232 bytes
    zero-lead            3 members      737617760 bytes
    empty                1 members              0 bytes
```

`MOV.BIN` is twenty MPEG-2 program streams and one empty index slot.
[→ 07](07-video-and-audio.md)

`DAT.BIN` is where the game lives. 11,036 of its members are raw SPU-ADPCM
sample banks, 1,312 are Tales-codec blocks, and of the 2,160 "raw" members
**744 are `SCPK` bundles** carried over unchanged from the 2002 title — which is
where most of the remaining compressed data hides. [→ 08](08-scpk-and-cab.md)

`FLD.BIN` is ten members and 819 MB. Three of them are 244, 243 and 251 MB and
begin with the same 36 zero bytes followed by the same IEEE-754 floats; six more
come in three pairs of **identical size but different content** — 13,565,136 /
13,565,136, 13,501,424 / 13,501,424, 13,921,056 / 13,921,056 — each pair opening
with the same 176-byte-strided offset table. Same layout, different data. What
the pairing means is unresolved. [→ 99](99-open-questions.md)

---

## Three levels of nesting, and how they differ

The disc has more than one container idea in it, and they do not agree with each
other. That is worth stating plainly rather than smoothing over.

**Level 1 — the executable's index.** 64-byte alignment, padding in the low six
bits of the offset, sizes implied by the next entry, one sentinel. Described
above.

**Level 2a — the bundle.** Some top-level members are a `u32` count followed by
that many `u32` offsets relative to the member, **each a multiple of 256**, with
the header padded out to the first of them; sizes are implied and the last
sub-member runs to the end. `DAT.BIN` member 23 is one: count 62, header 252
bytes padded to 256, and its 62 sub-members are 49 method-3 blocks, 2 method-1
blocks and 11 raw payloads.

**Level 2b — `SCPK`.** A four-byte magic, a version, a kind, a count, and then
`count` explicit `u32` **sizes** with the members concatenated with no padding at
all. 744 of these. This is the 2002 format, and `tools/scpk.py`'s parser is the
2002 pipeline's parser with no edits. [→ 08](08-scpk-and-cab.md)

**Level 2c — the pair archive.** A `u32` count followed by `count` × (`u32`
offset, `u32` size) pairs that tile the buffer end to end. `DAT.BIN` member 0
decompresses into one: three members, all `TIM2`, closing exactly on the 25,504
declared bytes.

Four different ways to say "here are N things", on one disc, from one team. None
of them carries a name for anything. Whatever named these assets stayed in the
build system.
