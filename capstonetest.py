# test1.py
from capstone import *

CODE = b"\x8d\x4c\x32\x08\x01\xd8"

md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True

for insn in md.disasm(CODE, 0x1000):
    print("%s\t%s" % (insn.mnemonic, insn.op_str))

    (regs_read, regs_write) = (insn.regs_read, insn.regs_write)

    if len(regs_read) > 0:
        print("\n\tRegisters read:", end="")
        for r in regs_read:
            print(" %s" % (insn.reg_name(r)), end="")
        print()

    if len(regs_write) > 0:
        print("\n\tRegisters modified:", end="")
        for r in regs_write:
            print(" %s" % (insn.reg_name(r)), end="")
        print()