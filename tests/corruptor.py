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


def distribute_random_amount(amount, bin_count):
    if bin_count == 1:
        return [amount]
    # TODO : Fail
    index = []
    result = [0] * bin_count
    for i in range(0, bin_count):
        k = random.randint(0, bin_count - 1)
        while k in index:
            k = random.randint(0, bin_count - 1)
        index.append(k)

    for i in range(0, bin_count):
        result[index[i]] = random.randint(0, amount)
        amount -= result[index[i]]
        if amount <= 0:
            break
    return result


def corrupt_instruction(program, original_instruction, address, conditional=True, registers=False, opcode=False, amount=2):
    # We corrupt an instruction
    bin_c = 1 if conditional else 0
    bin_c = bin_c + 1 if registers else bin_c
    bin_c = bin_c + 1 if opcode else bin_c
    amount = distribute_random_amount(amount, bin_c)
    corrupted = [original_instruction.encoding]
    if conditional:
        bin_c -= 1
        corrupted = corrupt_conditional(amount[bin_c], original_instruction.encoding)
    if registers:
        bin_c -= 1
        r = []
        for c in corrupted:
            r.extend([cc for cc in corrupt_registers(amount[bin_c], c) if cc not in r])
        corrupted = r
    if opcode:
        bin_c -= 1
        r = []
        for c in corrupted:
            r.extend([cc for cc in corrupt_opcode(amount[bin_c], c) if cc not in r])
        corrupted = r


    #program[address] = []
    for i in range(1, len(corrupted)):
        inst = DARMInstruction(corrupted[i])
        if inst.darm is not None:
            program[address].append(inst)

    return program[address]

