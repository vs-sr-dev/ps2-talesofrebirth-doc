# Tools

Python 3, **standard library only** — no dependencies to install, nothing to
declare. One file per job. Every one of them takes the disc image (or a file
extracted from it) as an argument and prints to standard output; the committed
output of each is in [`../reports/`](../reports/).

Nothing here writes to the image, and nothing here extracts game data by
default. `binfs.py --extract` and `iso9660.py --extract` exist for inspection and
are the only commands that write files.

```
python tools/<tool>.py            # every tool prints its own usage
```

---

## Copied, not written

Two files are deliberately not this repository's work, and that is the point.

| File | From | Status |
|---|---|---|
| `tales_block.py` | [tales-blockcodec-doc](https://github.com/vs-sr-dev/tales-blockcodec-doc) | **byte-identical.** The reference decoder for the shared block codec, copied without an edit. It decodes 2,851 of 2,851 blocks on this disc. A title that needed a patched decoder would be a new dialect; this one is not. |
| `scpk.py` | [ps2-talesofdestiny2-doc](https://github.com/vs-sr-dev/ps2-talesofdestiny2-doc) | `parse()`, `block_head()`, `cmd_census()` and `cmd_dupes()` are **copied unchanged**. Only the layer that locates bundles is new, because the index moved from `FILE.FPB` to this disc's three `.BIN` containers. Both files are published, so the claim is checkable. |

Run `python tools/tales_block.py --selftest` to confirm the decoder is intact
without needing any image.

---

## This disc's own tools

| File | What it does |
|---|---|
| `binfs.py` | The three `.BIN` containers and the index the executable carries for them. Locates each table by searching for a word equal to the container's length, then walking back — no hard-coded addresses. Decodes the 64-byte-aligned-offset / padding-in-low-six-bits encoding, classifies members from their own first bytes, and detects raw SPU-ADPCM by validating every frame header rather than by a magic number. `--tables`, `--census`, `--list`, `--extract`. |
| `codec_census.py` | Decodes every block the packer produced, at every level of nesting, and counts its habits. `--nested` follows `.BIN` bundles. `--scan` does the opposite job and sweeps a container for headers the index does **not** point at, with `--step` and `--budget`, and always prints how far it got and whether it stopped early. |
| `prefix_scan.py` | **The lineage instrument.** Longest identical byte run between one routine and a whole executable, at any alignment, found without being told where to look — rolling hash with a binary search on length, verified against real bytes. `--control` repeats the search with an unrelated routine of the same length, and is not optional: short runs occur by chance in any two MIPS routines. The corpus's 1997↔2000 pair reproduces at 212 bytes, which is how you know the instrument reads true. |
| `mpeg.py` | Reads the MPEG-2 sequence header of every movie in `MOV.BIN` — at the offsets the game's own index declares, so a wrong index would show up as a missing pack header. Width, height, aspect, frame rate and bit rate all come out of the bitstream. |
| `leftovers.py` | Pulls printable runs out of an executable and sorts them into categories that have paid off across this corpus — devkit paths, debug text, placeholders, SDK stamps, toolchain strings, save-file names. `--raw` turns the filter off so you can audit what it discarded. `--sweep` does the other half: searches the **whole disc image** byte by byte for thirty-one format signatures and cross-title names and prints the count for every one of them **including the zeros**, because most of this repository's negative results rest on it. |

## Inherited from the sibling pipelines

Unchanged except where noted; they do the same job here that they do there.

| File | From | What it does |
|---|---|---|
| `iso9660.py` | ps2-talesofdestiny2-doc | Volume descriptors and directory walk for a PlayStation 2 DVD. |
| `sector_map.py` | ps2-talesofdestiny2-doc | Accounts for every sector; `--slack` shows what nothing claims. |
| `ps2elf.py` | ps2-talesofdestiny2-doc | ELF header, sections, segments, symbols, `.iopmod`. |
| `dismips.py` | ps2-talesofdestiny2-doc | MIPS disassembler for EE and IOP alike. **Extended here** with the R5900 quadword `lq` / `sq`, because an Emotion Engine prologue is full of them and the 2004 dictionary clear is a quadword store — without them those listings read as a wall of `.word`. |
| `decoder_lineage.py` | ps2-talesofdestiny2-doc | Word-by-word comparison of two MIPS routines. Reported for completeness; **not used as evidence here**, because on these routines the real pairs and a deliberate control land in the same band. |
| `ring_sites.py` | gc-talesofsymphonia-doc | Scans for the `4078` / `4079` immediates on MIPS or PowerPC. Works in the negative too: no `4078` anywhere means no decoder. |
| `xarch.py`, `disppc.py` | gc-talesofsymphonia-doc | Routine-against-routine comparison across instruction sets. `xarch.py`'s cross-architecture similarity ratio is **not** cited anywhere in this repository — the corpus publishes it with its own negative control attached and it does not discriminate. Only its byte comparison is meaningful, and `prefix_scan.py` supersedes that by searching whole executables. `disppc.py` is the PowerPC half `xarch.py` imports. |

The sibling pipelines' `cvm.py`, `cab.py`, `census.py`, `manifest.py` and
`dupes.py` are **not carried here.** They are written against a GameCube image
or a CRI `CVM` volume, and this disc has neither — running them would mean
importing a GameCube reader to prove a negative that
[`leftovers.py --sweep`](../reports/magic-sweep.txt) proves directly, over the
whole image, in a minute. Everything in this repository runs against this
disc.

---

## Cost of the expensive commands

Measured on the 4.51 GB image, so you can decide before you start rather than
after:

| Command | Time |
|---|---|
| `binfs.py --census` | ~11 s cold, under 1 s warm |
| `codec_census.py --nested` | ~48 s |
| `scpk.py --census` | ~4 min (decodes 806 MB) |
| `codec_census.py --scan DAT.BIN --step 64` | ~3 min for all 1.93 GB |
| `leftovers.py --sweep` over the whole image | ~59 s |

`--scan` takes `--budget SECONDS` and prints `ABANDONED at N` if it stops early,
so a bounded run always says what it did not cover. It was not needed on this
disc: the top-level index tiles all three containers exactly, so nothing larger
than 63 bytes lies outside it, and that is arithmetic rather than a sweep.
