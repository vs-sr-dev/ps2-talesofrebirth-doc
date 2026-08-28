"""A small PowerPC disassembler, enough to read a decompressor.

The sibling pipelines disassemble MIPS with `dismips.py`.  The GameCube build
is the first in this corpus on a PowerPC, and the routine that has to be read
is a byte-shuffling loop: loads, stores, shifts, masks, compares, branches.
That is a small part of the instruction set, and this file covers it plus
enough of the rest to keep the listing honest.  Anything unrecognised prints
as a word rather than as a guess.

Big-endian, as the machine is.

    python tools/disppc.py FILE --at FILEOFF --va ADDR [count]
"""

import struct
import sys

SPR = {1: 'xer', 8: 'lr', 9: 'ctr'}

DFORM = {
    3: 'twi', 7: 'mulli', 8: 'subfic', 10: 'cmplwi', 11: 'cmpwi',
    12: 'addic', 13: 'addic.', 14: 'addi', 15: 'addis',
    24: 'ori', 25: 'oris', 26: 'xori', 27: 'xoris',
    28: 'andi.', 29: 'andis.',
    32: 'lwz', 33: 'lwzu', 34: 'lbz', 35: 'lbzu',
    36: 'stw', 37: 'stwu', 38: 'stb', 39: 'stbu',
    40: 'lhz', 41: 'lhzu', 42: 'lha', 43: 'lhau',
    44: 'sth', 45: 'sthu', 46: 'lmw', 47: 'stmw',
    48: 'lfs', 49: 'lfsu', 50: 'lfd', 51: 'lfdu',
    52: 'stfs', 53: 'stfsu', 54: 'stfd', 55: 'stfdu',
}
LOADS = {32, 33, 34, 35, 40, 41, 42, 43, 46, 48, 49, 50, 51}
STORES = {36, 37, 38, 39, 44, 45, 47, 52, 53, 54, 55}

X31 = {
    0: 'cmpw', 4: 'tw', 8: 'subfc', 10: 'addc', 11: 'mulhwu', 19: 'mfcr',
    20: 'lwarx', 23: 'lwzx', 24: 'slw', 26: 'cntlzw', 28: 'and',
    32: 'cmplw', 40: 'subf', 54: 'dcbst', 55: 'lwzux', 60: 'andc',
    75: 'mulhw', 83: 'mfmsr', 86: 'dcbf', 87: 'lbzx', 104: 'neg',
    119: 'lbzux', 124: 'nor', 136: 'subfe', 138: 'adde', 144: 'mtcrf',
    150: 'stwcx.', 151: 'stwx', 183: 'stwux', 200: 'subfze',
    202: 'addze', 215: 'stbx', 234: 'addme', 235: 'mullw',
    247: 'stbux', 266: 'add', 279: 'lhzx', 284: 'eqv', 311: 'lhzux',
    316: 'xor', 339: 'mfspr', 343: 'lhax', 371: 'mftb', 375: 'lhaux',
    407: 'sthx', 412: 'orc', 439: 'sthux', 444: 'or', 459: 'divwu',
    467: 'mtspr', 476: 'nand', 491: 'divw', 512: 'mcrxr', 533: 'lswx',
    534: 'lwbrx', 535: 'lfsx', 536: 'srw', 566: 'tlbsync', 567: 'lfsux',
    595: 'mfsr', 597: 'lswi', 598: 'sync', 599: 'lfdx', 631: 'lfdux',
    662: 'stwbrx', 663: 'stfsx', 695: 'stfsux', 725: 'stswi',
    727: 'stfdx', 759: 'stfdux', 790: 'lhbrx', 792: 'sraw',
    824: 'srawi', 854: 'eieio', 918: 'sthbrx', 922: 'extsh',
    954: 'extsb', 982: 'icbi', 983: 'stfiwx', 1014: 'dcbz',
}

BRANCH_HINT = {
    (12, 0): 'blt', (12, 1): 'bgt', (12, 2): 'beq', (12, 3): 'bso',
    (4, 0): 'bge', (4, 1): 'ble', (4, 2): 'bne', (4, 3): 'bns',
}


def _simm(v):
    return v - 0x10000 if v & 0x8000 else v


def disasm(w, pc):
    op = w >> 26
    rd = (w >> 21) & 31
    ra = (w >> 16) & 31
    rb = (w >> 11) & 31
    imm = w & 0xFFFF

    if w == 0x4E800020:
        return 'blr'
    if w == 0x4E800421:
        return 'bctrl'
    if w == 0x4E800420:
        return 'bctr'
    if w == 0x60000000:
        return 'nop'

    if op == 16:                                     # bc
        bo, bi = rd, ra
        off = _simm(w & 0xFFFC)
        tgt = (off if w & 2 else pc + off) & 0xFFFFFFFF
        key = (bo & 0x1E, bi & 3)
        name = BRANCH_HINT.get((key[0] if key[0] in (12, 4) else bo, key[1]))
        if name is None:
            name = 'bc %d,%d,' % (bo, bi)
            return '%s0x%08X' % (name, tgt)
        cr = bi >> 2
        return '%-8s %s0x%08X' % (name + ('l' if w & 1 else ''),
                                  ('cr%d, ' % cr) if cr else '', tgt)
    if op == 18:                                     # b
        off = w & 0x03FFFFFC
        if off & 0x02000000:
            off -= 0x04000000
        tgt = (off if w & 2 else pc + off) & 0xFFFFFFFF
        return '%-8s 0x%08X' % ('bl' if w & 1 else 'b', tgt)
    if op in DFORM:
        n = DFORM[op]
        if op in LOADS or op in STORES:
            return '%-8s r%d, %d(r%d)' % (n, rd, _simm(imm), ra)
        if op in (10, 11):
            return '%-8s r%d, %d' % (n, ra, _simm(imm) if op == 11 else imm)
        if op == 14 and ra == 0:
            return '%-8s r%d, %d' % ('li', rd, _simm(imm))
        if op == 15 and ra == 0:
            return '%-8s r%d, 0x%04X' % ('lis', rd, imm)
        if op in (24, 25, 26, 27, 28, 29):
            return '%-8s r%d, r%d, 0x%04X' % (n, ra, rd, imm)
        return '%-8s r%d, r%d, %d' % (n, rd, ra, _simm(imm))
    if op == 20:                                     # rlwimi
        return '%-8s r%d, r%d, %d, %d, %d' % ('rlwimi', ra, rd,
                                              rb, (w >> 6) & 31,
                                              (w >> 1) & 31)
    if op == 21:                                     # rlwinm
        sh, mb, me = rb, (w >> 6) & 31, (w >> 1) & 31
        if me == 31 and mb == 32 - sh and sh:
            return '%-8s r%d, r%d, %d' % ('srwi', ra, rd, 32 - sh)
        if mb == 0 and me == 31 - sh:
            return '%-8s r%d, r%d, %d' % ('slwi', ra, rd, sh)
        return '%-8s r%d, r%d, %d, %d, %d' % ('rlwinm', ra, rd, sh, mb, me)
    if op == 23:
        return '%-8s r%d, r%d, r%d' % ('rlwnm', ra, rd, rb)
    if op == 31:
        xo = (w >> 1) & 0x3FF
        n = X31.get(xo)
        if n is None:
            return '.word 0x%08X' % w
        if n == 'mfspr' or n == 'mtspr':
            s = ((w >> 16) & 0x1F) | (((w >> 11) & 0x1F) << 5)
            reg = SPR.get(s, 'spr%d' % s)
            return ('%-8s r%d, %s' % ('mfspr', rd, reg) if n == 'mfspr'
                    else '%-8s %s, r%d' % ('mtspr', reg, rd))
        if n == 'srawi':
            return '%-8s r%d, r%d, %d' % (n, ra, rd, rb)
        if n in ('cmpw', 'cmplw'):
            return '%-8s r%d, r%d' % (n, ra, rb)
        if n in ('extsb', 'extsh', 'cntlzw', 'neg'):
            return '%-8s r%d, r%d' % (n, ra, rd)
        if n in ('and', 'or', 'xor', 'nor', 'andc', 'orc', 'nand', 'eqv',
                 'slw', 'srw', 'sraw'):
            return '%-8s r%d, r%d, r%d' % (n + ('.' if w & 1 else ''),
                                           ra, rd, rb)
        if n.startswith('l') or n.startswith('st'):
            return '%-8s r%d, r%d, r%d' % (n, rd, ra, rb)
        return '%-8s r%d, r%d, r%d' % (n + ('.' if w & 1 else ''),
                                       rd, ra, rb)
    return '.word 0x%08X' % w


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    data = open(argv[1], 'rb').read()
    off = int(argv[argv.index('--at') + 1], 0) if '--at' in argv else 0
    va = int(argv[argv.index('--va') + 1], 0) if '--va' in argv else 0
    n = 40
    for a in argv[2:]:
        if a.isdigit():
            n = int(a)
    for i in range(n):
        w = struct.unpack_from('>I', data, off + 4 * i)[0]
        print('0x%08X  0x%08X  %s' % (va + 4 * i, w, disasm(w, va + 4 * i)))


if __name__ == '__main__':
    main(sys.argv)
