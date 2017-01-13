import random
import math
from semantic_codec.architecture.bits import Bits
from semantic_codec.architecture.darm_instruction import DARMInstruction


def corrupt_bits(hi, lo, amount, instruction):
    """
    Corrupt the bits in an instruction by fliping bits around
    :param hi: Corruption bit start
    :param lo:  Corruption bit end
    :param amount: Number of bits to corrupt
    :param instruction: Instruction to corrupt
    :return: Returns the original instruction, as well as all the others resulting from the corruption
    """
    # Generate random positions
    result, bits = [instruction], []
    while len(bits) < amount:
        x = random.randint(lo, hi)
        if x not in bits:
            bits.append(x)

    for i in range(1, 2 ** amount):
        noise, j, m = 0, 1, math.log(i, 2) + 1
        while j <= m:
            noise += Bits.on(bits[j - 1]) if j & i else 0
            j <<= 1
        result.append(instruction ^ noise)
    return result


def corrupt_conditional(amount, instruction):
    return corrupt_bits(31, 28, amount, instruction)


def corrupt_registers(amount, encoding):
    return corrupt_bits(10, 0, amount, encoding)


def corrupt_opcode(amount, encoding):
    return corrupt_bits(27, 20, amount, encoding)


def corrupt_instruction(program, original_instruction, address, conditional=True, registers=False, opcode=False):
    # We corrupt an instruction
    corrupted = [original_instruction.encoding]
    if conditional:
        corrupted = corrupt_conditional(2, original_instruction.encoding)
    if registers:
        r = []
        for c in corrupted:
            r.extend([cc for cc in corrupt_registers(2, c) if cc not in r])
        corrupted = r
    if opcode:
        r = []
        for c in corrupted:
            r.extend([cc for cc in corrupt_opcode(2, c) if cc not in r])
        corrupted = r


    #program[address] = []
    for i in range(1, len(corrupted)):
        inst = DARMInstruction(corrupted[i])
        if inst.darm is not None:
            program[address].append(inst)

