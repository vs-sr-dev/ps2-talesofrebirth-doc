# 06 — Decoder lineage

This is the document the disc was opened for.

Reproduce with:

```
python tools/ring_sites.py SLPS_254.50 --mips --base 0x00100000 --off 0x1000
python tools/prefix_scan.py SLPS_254.50 0x0010CDA8 932 SLPS_254.00 SLPS_251.72 \
       SLPS_030.50 SLPS_011.00 --control 0x001BFC34
python tools/dismips.py SLPS_254.50 --va 0x0010CDA8 68
```

Output: [`reports/ring-sites.txt`](../reports/ring-sites.txt),
[`reports/decoder-prefix.txt`](../reports/decoder-prefix.txt).

---

## The question

[tales-blockcodec-doc](https://github.com/vs-sr-dev/tales-blockcodec-doc)
records that Wolf Team's in-house LZSS was not merely reused between titles but
*recompiled from the same file*: 1997's *Tales of Destiny* and 2000's *Tales of
Eternia*, three years and two games apart on the same R3000A, share **212 bytes
of identical machine code** at the head of the routine. When the format reached
the PlayStation 2 in 2002 that test became unavailable — different CPU,
different compiler — and when *Tales of Symphonia* reached the same PlayStation 2
in 2004 the test became available again and returned nothing: **six bytes**, the
longest identical run at any alignment between the 2002 and 2004 decoders.

The corpus attributed part of that to a toolchain change, because `SLPS_254.00`
carries a `.comment` section reading `MW MIPS C Compiler (2.4.1.01)` and
`SLPS_251.72` carries no compiler string at all, and attributed the rest to a
hand edit, because the 2004 build replaced an inline dictionary clear bounded by
**4078** with a call to a quadword `bzero` taking **4080**. A compiler does not
change a constant.

*Tales of Rebirth* is the control that measurement wanted. Same studio, same
R5900, and **three months** after Symphonia's volume stamp. If the 2004 edit went
into a shared source file, it is still there. If the decoder had merely been
recompiled with a different toolchain, then anything else compiled from the same
sources with the same toolchain should show the same amount of drift — and that
is testable.

---

## The decoder is here, on both processors

The corpus's shortcut is to scan for the immediates **4078** and **4079**, which
are `RING − 18` and `RING − 17`, chosen by the packer rather than by the
programmer.

```
--- SLPS_254.50 (Emotion Engine, R5900)          8 sites
0x0010CA28   0x24020FEE addiu      4078  routine 0x0010C8F0 (+78 words)
0x0010CA30   0x24020FEF addiu      4079  routine 0x0010C8F0 (+80 words)
0x0010CCC8   0x24020FEE addiu      4078  routine 0x0010CB54 (+93 words)
0x0010CCCC   0x24020FEF addiu      4079  routine 0x0010CB54 (+94 words)
0x0010CDB4   0x24060FEF addiu      4079  routine 0x0010CD6C (+18 words)
0x0010CEE8   0x24070FEE addiu      4078  routine 0x0010CEB8 (+12 words)
0x0010D000   0x24080FEF addiu      4079  routine 0x0010CFD0 (+12 words)
0x001C5548   0x66040FEF daddiu     4079  routine 0x001C54E4 (+25 words)

--- BOOT.IRX (I/O processor, R3000A)             5 sites
--- IOPRP300.IMG                                 none
```

So the decoder is on the Emotion Engine **and** on the I/O processor. That is
the 2002 arrangement returning: *Destiny 2* carried a copy in `FILESYS.IRX`, and
the 2004 *Symphonia* dropped it — neither `IOPRP300.IMG` nor `IRXARC.BIN` on
that disc contains a `4078` anywhere. Rebirth puts it back. `IOPRP300.IMG` here
is nineteen stock Sony modules and contains no `4078` either; the copy is in
`BOOT.IRX`, the single custom module, which is called `IOPBOOT` version 1.1 and
whose only strings besides library imports are `SYSTEM.CNF`, `DAT.BIN`,
`MOV.BIN` and `FLD.BIN`.

### And both copies renumber the methods

The corpus records one place in four titles where the on-disc method byte is not
used directly: *Destiny 2*'s I/O processor copy dispatched on internal kinds
**2 and 4** instead of the disc's 1 and 3. On this disc **both** copies do it.
The Emotion Engine's header state machine reads the method byte, adds one,
stores it, and then:

```
0x0010CA04  11020006  beq   t0, v0, 0x0010CA20     ; v0 = 2
0x0010CA10  11020006  beq   t0, v0, 0x0010CA2C     ; v0 = 4
0x0010CA28  24020fee  addiu v0, zero, 4078
0x0010CA30  24020fef  addiu v0, zero, 4079
```

and `BOOT.IRX` does the same thing at its own `0x000036B0`. What was one
routine's quirk in 2002 is this title's convention.

---

## The strong test, and its controls

Two routines can be compared by aligning two known addresses, which is what
`xarch.py` and `decoder_lineage.py` do. That answers a narrower question than it
looks like: it cannot distinguish "recompiled and moved" from "not there", and
it cannot find a shared prefix that ended up somewhere else. `prefix_scan.py`
asks the whole-file version — take *N* bytes of A and find the longest run of
them that appears **anywhere** in B, at any alignment, without being told where
to look.

### The positive control passes

```
needle  SLPS_011.00  va 0x80150BB0  file 0xB13B0  560 bytes
longest run of those bytes appearing anywhere in:
  SLPS_030.50          212 bytes  (needle+0, SLPS_030.50+0x13D04)
```

Handed only 1997's address, searching the whole of 2000's executable, the tool
lands on **212 bytes** — the number the corpus reports from an entirely different
method. The instrument reads true.

### The measurement

Rebirth's decoder cluster is `ring_init` + the method-1 core + the method-3
core, 932 contiguous bytes from `0x0010CDA8`:

```
needle  SLPS_254.50  va 0x0010CDA8  file 0xDDA8  932 bytes
longest run of those bytes appearing anywhere in:
  SLPS_254.00           17 bytes     Tales of Symphonia,  PS2, 2004
  SLPS_251.72           13 bytes     Tales of Destiny 2,  PS2, 2002
  SLPS_030.50           12 bytes     Tales of Eternia,    PS1, 2000
  SLPS_011.00            9 bytes     Tales of Destiny,    PS1, 1997
```

Seventeen bytes, against 212 for the pair that is known to be one object. And
17 bytes lands at needle+261, inside the unrolled `(i, 0x00)` pattern fill —
four instructions of a loop whose shape is dictated by the format, not a
fragment of a shared prologue.

### The control that makes this different from 2004's result

The corpus had to hedge Symphonia's six bytes: a change of compiler could
explain them by itself, and there was no way to tell how much of the drift was
toolchain. On this disc there is. Take **the same 932 bytes' worth** of
Rebirth's own C runtime — the block beginning at `0x001BFC34`, which is `memset`
and the string routines that follow it — and run the identical measurement:

```
control: an unrelated routine of the same length, va 0x001BFC34
  SLPS_254.00          276 bytes  (needle+544, SLPS_254.00+0x254C0)
  SLPS_251.72          288 bytes  (needle+544, SLPS_251.72+0x91A04)
  SLPS_030.50           13 bytes
  SLPS_011.00           13 bytes
```

**276 contiguous identical bytes with Symphonia. 288 with Destiny 2.** And the
match is real code, not a run of zeros — here are the two sides at the point
where the match begins, an Emotion Engine SIMD string routine:

```
Rebirth  0x001BFE54  34c68080  ori   a2, a2, 0x8080     Symphonia  0x001253C0  34c68080
         0x001BFE58  00063438  .word 0x00063438                    0x001253C4  00063438
         0x001BFE5C  34c68080  ori   a2, a2, 0x8080                0x001253C8  34c68080
         0x001BFE60  00063438  .word 0x00063438                    0x001253CC  00063438
         0x001BFE64  34c68080  ori   a2, a2, 0x8080                0x001253D0  34c68080
         0x001BFE68  1520001f  bne   t1, zero, ...                 0x001253D4  1520001f
         0x001BFE6C  dca20000  ld    v0, 0(a1)                     0x001253D8  dca20000
```

All three PlayStation 2 games in the corpus link **the same C runtime objects,
byte for byte**. Whatever else changed between 2002, August 2004 and November
2004, the library did not, and neither did the ability to produce identical
bytes from identical source.

So the toolchain explanation is closed off by measurement rather than by
assertion. Two executables that share 276 bytes of runtime share **seventeen**
bytes of decoder. The decoder is not the same source.

### The I/O processor copies do not match either

Both `BOOT.IRX` (2004) and `FILESYS.IRX` (2002) are R3000A relocatable modules,
so byte equality was available there too:

```
needle  BOOT.IRX  va 0x000034D4  900 bytes
  FILESYS.IRX           47 bytes
control: 900 bytes of BOOT.IRX's own module boilerplate
  FILESYS.IRX           46 bytes
```

Forty-seven against a control of forty-six. The two IOP decoders share nothing
beyond what any two IRX modules share.

---

## A third way to clear the dictionary

The strongest evidence is not the byte counts, it is the constant, because a
constant is a decision.

Every build from 1997 through 2003 clears the 4,096-byte ring with an inline
byte loop bounded by **4078**:

```
Tales of Destiny 2, 2002, 0x0010A1B0
  0x0010A1BC  24040fee  addiu a0, zero, 4078
  0x0010A1C0  00e91821  addu  v1, a3, t1
  0x0010A1C4  25290001  addiu t1, t1, 1
  0x0010A1C8  a0600000  sb    zero, 0(v1)
  0x0010A1CC  0124102a  slt   v0, t1, a0
  0x0010A1D4  1440fffa  bne   v0, zero, 0x0010A1C0
```

*Tales of Symphonia*'s 2004 port calls a hand-written quadword `bzero` with
**4080**, which is 4,078 rounded up to a multiple of sixteen so the Emotion
Engine's 128-bit store can be used:

```
Tales of Symphonia, 2004, 0x001C9820        and its callee 0x001DF090
  0x001C984C  24050ff0  addiu a1, zero, 4080    0x001DF094  srl a1, a1, 4
  0x001C9850  0c077c24  jal   0x001DF090        0x001DF098  sq  zero, 0(a0)
  0x001C9854  0200202d  daddu a0, s0, zero      0x001DF0A0  addiu a0, a0, 16
```

*Tales of Rebirth* does neither. It calls the **ordinary C library `memset`**
with **4079**, out of a routine that exists in no other build in the corpus —
a factored `ring_init` that both method variants share:

```
Tales of Rebirth, 2004, 0x0010CDA8
  0x0010CDA8  27bdffe0  addiu sp, sp, -32
  0x0010CDAC  0000282d  daddu a1, zero, zero      ; fill byte 0
  0x0010CDB0  7fb00010  sq    s0, 16(sp)
  0x0010CDB4  24060fef  addiu a2, zero, 4079      ; length
  0x0010CDBC  0c06ff0d  jal   0x001BFC34          ; memset
  0x0010CDC0  0080802d  daddu s0, a0, zero
```

and the callee at `0x001BFC34` is not a hand-written quadword loop at all, it is
the library's general `memset`, with an alignment test, a 32-byte quadword body
and a byte-at-a-time fallback for lengths under eight.

**And `4080` does not appear in this executable.** A scan of all 204,024
instruction words of `.text` for an immediate of 4,080 in any I-type opcode
returns exactly one hit, `andi a2, v0, 0x0FF0` at `0x0014C794` — a bit mask, not
a length. The signature the corpus named as "the source fingerprint, independent
of the compiler" is absent from a build three months later on the same CPU at
the same studio.

### Why 4079 and not 4078

Because this build only has one clear. The corpus records that the ring cursor
starts at `RING − F`, where `F` is the longest match the variant can encode: 18
for method 1, so 4078, and 17 for method 3, so 4079. Every earlier build clears
4,078 bytes inside each of two separate decode routines. Rebirth factors the
setup out into one routine that both call, so it has to clear enough for the
higher of the two cursors — 4,079. The two cursors themselves are unchanged and
still appear as immediates in their own routines:

```
0x0010CEE8  24070fee  addiu a3, zero, 4078      ; method 1 core, cursor
0x0010D000  24080fef  addiu t0, zero, 4079      ; method 3 core, cursor
```

That is a refactor of the source, not a compiler artefact. It has a
consequence a compiler could not produce — the number 4,079 in a place where
every previous build wrote 4,078 — and it explains itself.

---

## Everything the source still chooses is unchanged

None of this is a new dialect. The format did not move; only the code around it
did. From the disassembly:

| Trait | Rebirth 2004 |
|---|---|
| Control register refill | `ori t1, v0, 0xFF00` at `0x0010CF10` — unchanged since 1997 |
| Ring mask | `andi a3, a3, 0x0FFF` at `0x0010CF34` |
| Length nibble | `andi v0, a1, 0x000F` — the 1997 PlayStation order |
| Reference top nibble | `andi v1, a1, 0x00F0` then `sll v1, v1, 4` |
| `(i, 0x00)` preload | 256 iterations, **unrolled by eight** |
| `(i, 0xFF)` preload | 256 iterations, **unrolled by seven** |
| Cursors | 4078 / 4079 |
| Header | nine bytes, little-endian |

And the decisive test is the census: **1,312 top-level blocks, 1,488 blocks
inside `SCPK` bundles and 51 inside `.BIN` bundles — 2,851 blocks in total — all
of which decode to their declared length under `tales_block.py` copied from the
corpus with no edits and no Rebirth branch.** [→ 05](05-block-codec.md)

---

## What this means

The corpus's open question read: *was the source ever edited after 1997?*
Answered yes, once, in 2004. This disc changes the shape of that answer.

**Outcome B, from the session's framing.** There is no shared prefix. And
because the C runtime *is* shared for 276 and 288 bytes across the same pair of
files, the absence is not a toolchain artefact — it is the decoder specifically.

Three PlayStation 2 builds from one studio inside thirty months clear the same
4,096-byte array three different ways, with three different constants, through
three different mechanisms — inline `4078`, a bespoke quadword `bzero` with
`4080`, a library `memset` with `4079` — while every byte of the on-disc format
stays put. The right reading is no longer "the source was edited once in 2004".
It is that by 2004 **there was no longer one copy of the source to edit**. Each
title had its own, each was maintained by whoever was on that title, and what
they had in common was the format and the packer rather than the file.

Which raises the packer, since it is now the only thing that provably did not
fork. [→ 05](05-block-codec.md), [→ 99](99-open-questions.md)

---

## What was not measured, and why

The opcode-sequence similarity in `decoder_lineage.py` is reported in
[`reports/`](../reports/) for completeness but is **not used as evidence here**.
On this pair it scores 45.7% for Rebirth's method-1 core against Symphonia's,
28.9% for Rebirth's Emotion Engine state machine against its own I/O processor
one, and **22.1% for a deliberately unrelated control** — Rebirth's method-3
core against the first routine in `BOOT.IRX`. The real pairs and the control
land in the same band, so on these routines the measure does not discriminate,
exactly as tales-blockcodec-doc section 7 warns for the cross-instruction-set
case. The byte comparison and the constants are what carry the argument.

`xarch.py`'s cross-architecture ratio is not used at all, for the same reason
and on the corpus's own instruction.
