# 09 — Leftovers

Reproduce with:

```
python tools/leftovers.py SLPS_254.50 BOOT.IRX
python tools/binfs.py IMAGE.iso --census
```

Output: [`reports/leftovers.txt`](../reports/leftovers.txt).

`SLPS_254.50` is a clean build by the standards of this corpus. A filtered sweep
— eight characters or more, at least half letters, restricted alphabet — returns
**475 text runs** out of 1.28 MB, against the thousands a naive `strings` would
produce from MIPS code that happens to sit in the printable range. There is no
build path, no source file name, no `.c` or `.obj`, no assertion text, no
programmer's name. What is here is here for a reason, which makes each item
worth reading.

---

## 1. The whole cast, in English, on a Japan-only disc

At `0x00111A48` in `.rodata`, eight-byte slots, **surname then given name**:

```
Lindblum ........ Agarte
Bennett  ........ Claire
Rhambling ....... Hilda
Crowe    ........ Tytree
Barrs    ........ Annie
Gallardo ........ Eugene
Mao
Lungberg ........ Veigue
```

*Tales of Rebirth* has never been released outside Japan — no English, no
European, no Korean SKU, and no official localisation of any kind in the
twenty-one years since. The disc nonetheless carries a complete romanised name
table for the playable cast and the principal antagonists, in a fixed-width
layout that something indexes.

Immediately after it, the same region holds the Japanese names in Shift-JIS, and
immediately after *those*, at `0x00111B10`, the string **`MINI GAME 3`** —
a third minigame, in a build whose section table names exactly two,
`.minigame1_end` and `.minigame2_end`. [→ 99](99-open-questions.md)

## 2. Thirty-eight place names, also in English

At `0x0012AAF8` onward, one per 40- to 88-byte slot:

```
Cyglorg's Chambers    Yuris' Realm           Whirlpool
Farm Fresh Groceries  Flame-holder           Balka Prison
Mesechina Cavern      Balka harbor           Rabbitz Village
Tower of Nereg        Mocrado Village        Lenpao Sky Garden
Mount Sovereign       Shrine of Gilione      Shrine of Wontiga
Shrine of Eephon      Shrine of Fenia        Karez south side
Karez north side      Nereg Hostel           Kyogen Hostel
Toyohose Hostel       Forest Labyrinth west side / north side
Great Pokunan Bridge  Etoray Bridge          Great Larulen Bridge
Southern / Northern Alvan Mountains          Tel Alla Hostel
Razilda Harbor        Belsas Harbor          Babilograd Harbor
Babilograd            Climbers' Cavern       Anikamal
Keketto Hostel        Sannytown              Petnadjanka
Zeren Wetlands Spring The Burning Tower      The Bayo Plains Tower
Stone Ruins           The Hidden Chambers    Kurodadaku Desert
```

`Farm Fresh Groceries` is not a place name a translator would produce; it is a
developer's label for a shop map. `Balka harbor` and `Karez south side` are
lower-cased where the others are not. These are internal identifiers written in
English by the team, not a localisation, and they shipped.

## 3. About a hundred battle-effect names, several misspelled

`MAD SEAL`, `LIFE SEAL`, `BERSERK SEAL`, `NEGATIVE_SEAL`, `CURSED FORM`,
`SUMMON FORM`, `MENTAL BLOOD`, `ROUSE BLOOD`, `DASH ARMED`, `FEATHER ARMED`,
`RISE DRAIN`, `SHIELD DRAIN`, `RAPID SHOOT`, `HIND STEP`, `THRUST ATTACK`,
`SMASH POINT`, `PENETRATE`, `VANISH DRAIN`, `DACOITY ITEM`, `ROBBER ITEM`…

with, among them:

| shipped | intended |
|---|---|
| `INPACT /2`, `INPACT *2` | impact |
| `AUTO DEFFEND` | defend |
| `REGIST DRAIN`, `REGIST UP`, `MINUS REGIST` | resist |
| `SORN DAMAGE` | thorn |
| `NEGATIVE_SEAL` | the only one with an underscore, in a list of ninety-odd that use spaces |

`DACOITY` is a real word — an Anglo-Indian term for armed robbery — sitting next
to `ROBBER ITEM`, which does the same job in plainer language. Somebody reached
for a dictionary once.

## 4. `BISLPS-00000ToRsv%02d`

The memory-card code carries two format strings, adjacent:

```
0x00112AA0  BISLPS-25450ToRsv%02d
0x00112AB8  BISLPS-00000ToRsv%02d
```

The first is the real save directory name — `BI` plus the product code plus the
title's own tag. The second is the same string with the **product code left as
five zeroes**, which is what a template looks like before the title is assigned
one. Both are in the shipped executable, eight bytes apart, and one of them can
never match a real card.

Around them: `BISLPS-25450ToRsv??` (the wildcard used to enumerate saves),
`ToR_save`, `icon.ico`, `icon.sys`, and the card-status strings `NOCARD`,
`PS1(128KB)`, `PDA(POCKET STATION)`, `UNFORMAT`, `EXIST`. The PocketStation
string is standard Sony library text; it is not evidence of a PocketStation
feature.

## 5. `initialize debug window`

At `0x00111B78`, in a run of initialiser labels:

```
initialize debug window
initialize field res data
initialize actinfo
initialize res chr
```

Three of those four are the game booting. The first is a debug window, and it is
initialised in the same list as the other three in the retail build.

## 6. The devkit is still reachable

```
0x001122C0  fatal : '%s' is not found
0x001122E8  host0:
```

`host0:` is the PlayStation 2 devkit's host file system — the developer's PC,
mounted over the debug link. It sits in the same string pool as the
file-not-found error. Whatever fallback path led there was not compiled out.

Alongside it, from the CD/DVD driver: `Path table Cache ON:%d`,
`cd_read: error code %x`, `Ptbl_WCache:write %d`, `path_tbl_init Error %d`,
`pfs.host`.

## 7. The decoder names itself in an error message

```
0x0012D330  [CommonEffectDraw] sc-decode buffer over!!
```

A bracketed subsystem tag, a lower-case `sc-decode`, and two exclamation marks.
This is the only string on the disc that refers to the decompressor, and it is a
buffer-overrun diagnostic in the effect renderer. Next to it:

```
menu: common data error ! C(%d) SCFOM(%d)
fatal : heap area allocatio error!!
ToRHeapCheckToR
picture total : %d
adpcm total : %d
@src all use
```

`allocatio` is missing its final `n`. `ToRHeapCheckToR` is the heap guard, named
with the title's tag at both ends. `picture total` and `adpcm total` are the
loader's resident-asset counters, and they are the two words the team used for
the two things `DAT.BIN` is mostly made of. [→ 07](07-video-and-audio.md)

## 8. Seventy-three identifiers in group 99

At `0x00112EA2`, seventy-three eight-character identifiers on a 16-byte stride,
**descending**:

```
CHT99X99  CHT99X98  CHT99X97  ...  CHT99X29  CHT99X28  CHT99X27
```

They are contiguous — 99 down to 27, no gaps — and they are the **only**
`CHT`-prefixed identifiers in the executable; there is no `CHT01`, no `CHT02`,
nothing else. A production content table numbered from 27 to 99 inside a group
called 99, with no group 1 to 98 anywhere, is not production content. The word
immediately before the table is `notice`.

## 9. Empty index slots

The container indexes carry entries of length zero, which the loader can address
and which point at nothing:

* **`MOV.BIN` slot 0** — the first entry of the movie table, ahead of all twenty
  real movies.
* **`FLD.BIN` slot 0** — likewise.
* **`DAT.BIN`: 359 empty slots** out of 14,981.

A zero-length entry is not padding; the index is a dense array and every slot
costs four bytes whether it is used or not. 359 of them means 359 asset numbers
the build reserved and did not fill — or filled and later emptied. There is no
way to tell which from the disc, but the count is large enough to be a policy
rather than an accident, and the fact that both `MOV.BIN` and `FLD.BIN` reserve
**slot 0 specifically** suggests index 0 was a null sentinel by convention.

## 10. Five battle overlays with identical extents

`.battle_b008_end`, `.battle_b018_end`, `.battle_b025_end`, `.battle_b030_end`
and `.battle_b031_end` all end at exactly `0x00358D70` — the lowest address of
the thirty-two battle end markers. Same end address means same extent. Whether
they are the five smallest real battle modules or five that were never filled in
is not answerable from the section table. [→ 99](99-open-questions.md)

## 11. `unknvma`

Two of the sixteen vector-unit overlay sections are named

```
.DVP.overlay..unknvma.6545123.496.1
.DVP.overlay..unknvma.6526179.525.1
```

`unknvma` is Sony's `dvp-as` saying it could not resolve a virtual address. The
assembler wrote its own uncertainty into the section name, the linker kept the
name, and the name shipped.

---

## What is *not* here, which is itself a result

This corpus has a habit of cross-title contamination. *Tales of Destiny 2*'s disc
carries a complete promo build of Namco's *Venus & Braves*. *Tales of
Symphonia*'s executable names its movies `tod2_cut.h4m`, after a different game,
and its retail disc ships `BTLrutee.cab` — the battle archive for Rutee Katrea,
heroine of *Tales of Destiny* (1997) — built four and a half months before every
other archive on the disc.

Rebirth carries **nothing from another title.** A sweep of all 4,508,516,352
bytes for `Symphonia`, `symphonia`, `destiny`, `DESTINY`, `tod2`, `top2`,
`rebirth` and `REBIRTH` returns **zero hits each**. The uppercase `TOD2` and
`TOP2` do occur — three and twenty-six times — but every occurrence is inside
high-entropy compressed or ADPCM payload, none in any string table, and two of
the `TOD2` hits sit in byte-identical surroundings because they are inside
duplicated data. Four arbitrary bytes are expected to coincide roughly once per
gigabyte, and 4.5 GB of compressed data is where that happens.

So the one habit that held across two previous discs does not hold here. This
disc contains exactly one game and mentions exactly one game.
