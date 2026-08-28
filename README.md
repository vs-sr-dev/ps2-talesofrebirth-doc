# Tales of Rebirth (PlayStation 2, 2004, Japan) — structural documentation

Reverse-engineering notes on **SLPS-25450**, the Japan-only PlayStation 2
release of Namco Tales Studio's *Tales of Rebirth* (16 December 2004), whose
disc is stamped **2004-11-17 21:50:12**.

This repository is **documentation and analysis only**. It contains no disc
image, no extracted asset, no executable, no patch and no translation. There is
no porting, BYOA or modding intent. Every number quoted was produced by running
the tools in [`tools/`](tools/) on an image supplied separately, and their output
is committed under [`reports/`](reports/) so the claims can be checked without
owning the disc.

---

## TL;DR

| | |
|---|---|
| Product code | **SLPS-25450**, `VER = 1.02`, NTSC |
| Media | one **single-layer** DVD — 2,201,424 sectors, **4,508,516,352 bytes** |
| Volume | ISO 9660 + UDF bridge; publisher `NAMCO LTD.`, **volume identifier blank** |
| File system | **seven files, zero directories** |
| Executable | `SLPS_254.50`, R5900, 1,281,336 bytes, **section table intact**, no `.comment` |
| I/O processor | `IOPRP300.IMG` (19 stock Sony modules) + `BOOT.IRX` (`IOPBOOT` 1.1) |
| Containers | `MOV.BIN` / `DAT.BIN` / `FLD.BIN` — headerless, indexed **from the executable** |
| Index encoding | 64-byte-aligned offsets, **padding in the low six bits** — `FILE.FPB`'s 2002 encoding |
| Block codec | **yes**, on **both** processors — **2,851 of 2,851 blocks decode** |
| Bundles | **744 `SCPK`**, read by the 2002 pipeline's parser unchanged |
| `MSCF` / `CVMH` / `ROFSBLD` | **zero occurrences in 4.5 GB** |
| Disc used | **99.52%**, no separation hole |

### Five answers

**1 — The decoder forked, and this time the toolchain cannot explain it.** The
longest identical byte run between Rebirth's decoder and *Tales of Symphonia*'s
PlayStation 2 build, at any alignment anywhere in either file, is **17 bytes**.
The corpus's positive control — 1997's decoder searched for in 2000's whole
executable — reproduces at **212 bytes** through the same tool. And the control
that makes this new: **932 bytes of Rebirth's C runtime, measured identically,
matches Symphonia for 276 contiguous bytes and *Tales of Destiny 2* for 288.**
All three PlayStation 2 titles link the same runtime objects byte for byte, so
byte equality was demonstrably available and the decoder demonstrably did not
take it. [→ 06](docs/06-decoder-lineage.md)

**2 — Three builds, three ways to clear one array.** 1997–2003 clear the ring
with an inline byte loop bounded by **4078**. Symphonia 2004 calls a hand-written
quadword `bzero` with **4080**. Rebirth 2004 calls the ordinary library `memset`
with **4079**, from a *factored* `ring_init` that both method variants share and
that exists in no other build. **`4080` appears nowhere in this executable** —
one `andi` mask and nothing else. The corpus's "source fingerprint, independent
of the compiler" is absent three months later on the same CPU at the same studio.
The right reading is no longer *the source was edited once in 2004*; it is that
by 2004 **there was no longer one copy of the source to edit**.
[→ 06](docs/06-decoder-lineage.md)

**3 — Neither CVM nor FPB, and the 2002 mechanism is what survived.** No `CVMH`,
no `ROFSBLD`, no `SAMPLE_GAME_TITLE`, no CRI middleware of any kind: Symphonia's
nine-volume ROFS file system, three months old, is completely gone. There is no
`FILE.FPB` either. Instead there are three headerless `.BIN` blobs with three
`u32` tables in `.data` — and the entries use `FILE.FPB`'s exact encoding,
**64-byte-aligned offsets with each member's trailing padding packed into the low
six bits**. So the CVMs were an artefact of Symphonia's GameCube port, and the
studio's own habit is the 2002 one. [→ 03](docs/03-containers.md)

**4 — `SCPK` lived and `MSCF` never existed here.** 744 `SCPK` bundles holding
378 MB, parsed by the 2002 pipeline's `parse()` and `block_head()` **copied
without an edit**; exactly one `MFH` and exactly one `THEIRSCE` in every one of
them (plus 85 more `THEIRSCE` outside the bundles entirely); and **46.3% of
bundle bytes are copies** of bytes in other bundles, which
is what buying one seek per scene costs. Meanwhile a sweep of all
4,508,516,352 bytes finds **zero `MSCF`** — so the corpus's largest unidentified
format gains no samples and gains instead the information that it was never a
studio convention. [→ 08](docs/08-scpk-and-cab.md)

**5 — A full disc still leaves no separation hole.** Symphonia PS2 left 16.12%
of its disc empty, 686 MB in one interior gap, read as head separation and
published as unproven. Rebirth leaves **0.478%**, all of it after the last file,
with the seven files **contiguous end to end** and none at a round LBA. The
interior gap is not a studio layout policy. What *is* policy costs nothing:
1.73 GB of video occupies the entire inner region, then data, then field.
[→ 02](docs/02-disc-and-volume.md)

### And the archaeology

The executable carries **the whole cast romanised into English** — `Lungberg` /
`Veigue`, `Gallardo` / `Eugene`, `Rhambling` / `Hilda`, `Barrs` / `Annie`,
`Crowe` / `Tytree`, `Bennett` / `Claire`, `Lindblum` / `Agarte`, `Mao` — surname
first in eight-byte slots, in a game that has never been published outside Japan;
**thirty-eight place names in English** including `Farm Fresh Groceries`; and
about a hundred battle-effect names with `INPACT *2`, `AUTO DEFFEND` and
`REGIST UP` among them. The memory-card code has the real save string and, eight
bytes later, **`BISLPS-00000ToRsv%02d`** with the product code left as zeroes.
There is an `initialize debug window`, a `fatal : '%s' is not found` whose
fallback is the devkit's **`host0:`**, a `[CommonEffectDraw] sc-decode buffer
over!!` that names the decoder, a heap guard called `ToRHeapCheckToR`, a
`MINI GAME 3` in a build with two minigame overlays, seventy-three identifiers in
a group numbered 99 with no groups 1–98, **359 empty index slots**, and two
vector-unit overlays whose section names contain `unknvma` because the assembler
could not resolve an address and said so. And — for the first time in three discs
— **nothing from any other title**. [→ 09](docs/09-leftovers.md)

Start at [docs/01-overview.md](docs/01-overview.md).

---

## Claim status

| Claim | Status | Where |
|---|---|---|
| Single layer, 2,201,424 sectors | **Verified** — from the volume descriptor, not the file size | [02](docs/02-disc-and-volume.md) |
| Seven files, zero directories, contiguous end to end | **Verified** | [02](docs/02-disc-and-volume.md) |
| 0.478% slack, all after the last file; no interior gap | **Verified** | [02](docs/02-disc-and-volume.md) |
| The three index tables, located by sentinel without hard-coded addresses | **Verified** | [03](docs/03-containers.md) |
| Index encoding: 64-byte alignment, padding in the low six bits | **Verified** — closes to the byte on two members with independent internal lengths | [03](docs/03-containers.md) |
| The indexes tile all three containers exactly | **Verified** — arithmetic, not a sweep | [03](docs/03-containers.md) |
| 2,851 of 2,851 blocks decode under the unmodified corpus decoder | **Verified** | [05](docs/05-block-codec.md) |
| Zero method-0 blocks; largest block 1,015,400 bytes | **Verified** | [05](docs/05-block-codec.md) |
| Decoder present on both CPUs; both dispatch on kinds 2 and 4 | **Verified** | [06](docs/06-decoder-lineage.md) |
| 17-byte longest run vs Symphonia; 212-byte positive control reproduces | **Verified** | [06](docs/06-decoder-lineage.md) |
| 276 / 288 identical C-runtime bytes across the three PS2 titles | **Verified** — listings of both sides published | [06](docs/06-decoder-lineage.md) |
| `4080` absent from `SLPS_254.50`; `ring_init` clears 4,079 via library `memset` | **Verified** | [06](docs/06-decoder-lineage.md) |
| …and that this means the decoder source had forked per title | *Consistent* — the strongest reading of the measurements, not a proof | [06](docs/06-decoder-lineage.md), [99](docs/99-open-questions.md) |
| Zero `MSCF`, `CVMH`, `ROFSBLD`, `VAGp` in the whole image | **Verified** | [08](docs/08-scpk-and-cab.md) |
| 744 `SCPK` bundles; 2002 parser unchanged; 46.3% duplication | **Verified** | [08](docs/08-scpk-and-cab.md) |
| 20 movies, 640×448, 29.97 fps, 9 Mbit/s | **Verified** — from the sequence headers | [07](docs/07-video-and-audio.md) |
| 11,036 SPU-ADPCM members, 1,297,725,472 bytes | **Verified** — every frame header in the first 4 KB legal; 112 candidates rejected | [07](docs/07-video-and-audio.md) |
| The English cast, place and effect name tables | **Verified** | [09](docs/09-leftovers.md) |
| No cross-title data of any kind | **Verified** — `TOD2`/`TOP2` hits are all inside high-entropy payload | [09](docs/09-leftovers.md) |
| `THEIRSCE` is a scenario script | *Open* — one per bundle, text-sized, undecoded | [99](docs/99-open-questions.md) |
| The five same-extent battle overlays are stubs | *Open* | [99](docs/99-open-questions.md) |
| What Symphonia's 686 MB gap meant | *Open* — this disc rules out "studio policy" and nothing more | [99](docs/99-open-questions.md) |
| Opcode-sequence similarity as lineage evidence | **Not used** — real pairs and control land in the same band here | [06](docs/06-decoder-lineage.md) |

---

## Documents

| | |
|---|---|
| [01 — Overview](docs/01-overview.md) | the disc in one screen, the five answers, where to go |
| [02 — The disc and the volume](docs/02-disc-and-volume.md) | single layer from the volume, sector accounting, the layout question |
| [03 — The three containers](docs/03-containers.md) | `.BIN`, the index in `.data`, the padding encoding, four kinds of nesting |
| [04 — The executables](docs/04-executable.md) | 94 sections, the overlay map, VU overlays, SDK stamps, the IOP side |
| [05 — The block codec on this disc](docs/05-block-codec.md) | the census, the packer's habits, the vanished stored path |
| [06 — Decoder lineage](docs/06-decoder-lineage.md) | **the headline**: the measurement, its controls, and what it means |
| [07 — Video and audio](docs/07-video-and-audio.md) | 20 MPEG-2 streams, 1.30 GB of SPU-ADPCM, 67.2% of the disc |
| [08 — `SCPK`, and the `.cab` that is not here](docs/08-scpk-and-cab.md) | continuity with 2002, and a clean negative |
| [09 — Leftovers](docs/09-leftovers.md) | the archaeology, in full |
| [99 — Open questions](docs/99-open-questions.md) | twelve of them, each with its measurement |

## Reports

Committed output of every tool run: [`reports/`](reports/) — volume and sector
map, container tables and census, codec census and whole-disc totals, `SCPK`
census and duplication, decoder prefix scans with controls, ring-site scans
across six executables, the overlay map, movie parameters, the orphan sweep, the
string sweep, and the reference decoder's self-test.

## Tools

Python 3, standard library only, one file per job: [`tools/`](tools/) — see
[`tools/README.md`](tools/README.md). `tales_block.py` is copied from
[tales-blockcodec-doc](https://github.com/vs-sr-dev/tales-blockcodec-doc) without
a single edit, and `scpk.py`'s parser is copied from
[ps2-talesofdestiny2-doc](https://github.com/vs-sr-dev/ps2-talesofdestiny2-doc)
without a single edit. That both still work is a result, not a convenience.

## Related

* [tales-blockcodec-doc](https://github.com/vs-sr-dev/tales-blockcodec-doc) — the
  shared codec specification and lineage, across seven builds and four consoles
* [gc-talesofsymphonia-doc](https://github.com/vs-sr-dev/gc-talesofsymphonia-doc) — 2003 GameCube + 2004 PlayStation 2
* [ps2-talesofdestiny2-doc](https://github.com/vs-sr-dev/ps2-talesofdestiny2-doc) — 2002, `FILE.FPB` and `SCPK`
* [ps1-talesofeternia-doc](https://github.com/vs-sr-dev/ps1-talesofeternia-doc) — 2000
* [ps1-talesofdestiny-doc](https://github.com/vs-sr-dev/ps1-talesofdestiny-doc) — 1997
* [snes-talesofphantasia-doc](https://github.com/vs-sr-dev/snes-talesofphantasia-doc) — 1995 + GBA 2003

## Licence

Tools under [MIT](LICENSE). Documentation and reports under
[CC BY 4.0](LICENSE-DOCS).
