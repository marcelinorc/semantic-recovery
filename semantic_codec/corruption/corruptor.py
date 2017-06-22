import random
import math
import json
import sys

from semantic_codec.architecture.bits import Bits
from semantic_codec.architecture.darm_instruction import DARMInstruction
from semantic_codec.architecture.instruction import Instruction


class InstructionEncoder(json.JSONEncoder):
     def default(self, obj):
         if isinstance(obj, Instruction):
             return obj.encoding
         # Let the base class default method raise the TypeError
         return json.JSONEncoder.default(self, obj)


def save_corrupted_program_to_json(program, file_path):
    """
    Saves a corrupted program into a JSON file
    :param program:
    :param file_path:
    :return:
    """
    with open(file_path, "w") as json_file:
        json.dump(program, json_file, cls=InstructionEncoder, ensure_ascii=False, indent=2)


def load_corrupted_program_from_json(file_path):
    with open(file_path) as data_file:
        data = json.load(data_file)
    result = {}
    for k, v in data.items():
        result[int(k)] = v
        for i in range(0, len(v)):
            v[i] = DARMInstruction(v[i])
    return result


def corrupt_all_bits(lo, hi, instruction):
    """
    Corrupt all the bits from a given instruction from lo to hi bits
    :param hi: Hi bit to corrupt
    :param lo: Lo bit to corrupt
    :param instruction: Instruction to corrupt
    :return: the list of corrupted instructions
    """
    result = [instruction]
    for i in range(lo, hi):
        k = len(result)
        mask = Bits.on(i)
        for j in range(0, k):
            result.append(result[j] ^ mask)

    return result

def corrupt_all_bits_tuples(tuples, instruction):
    """
    Corrupt all the bits expressed as a list of (hi, lo) tuples in a given instruction.
    Lazy me, this routine assumes that the hi and lo bits of the tuples do not intersect, i.e. 0, 2 and 1, 3 produces
    unexpected results
    :param tuples: Bits to corrupt
    :param instruction: Instruction to corrupt
    :return: the list of corrupted instructions
    """
    result = [instruction]
    for t in tuples:
        l, h = t
        Bits.check_range(l, h)
        for i in result:
            all = corrupt_all_bits(l, h, i)
            for c in all:
                if c not in result:
                    result.append(c)
    return result


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


def corrupt_program(program, err_percent, max_amount):
    """
    Corrupts a program.
    :param program: Program to corrupt
    :param err_percent: Percentage of instructions to be corrupted from 0 - 100.
                        The routine will always corrupt at least one instruction with one bit of error
    :param max_amount: Maximal amount of bit errors per instructions, meaning that each corrupted instructions can
                       have up to this amount of errors
    """
    if 0 > err_percent > 100:
        raise RuntimeError("Percent cannot be larger than 100 or lower than 0")

    max_amount = max(1, max_amount)
    err_percent /= 100

    len_program = len(program)

    corrupted_amount = math.ceil(max(1, len_program * err_percent))

    # Find the min and max address in the program
    min_addr = sys.maxsize
    max_addr = -sys.maxsize
    for k in program:
        min_addr = k if min_addr > k else min_addr
        max_addr = k if max_addr < k else max_addr

    while corrupted_amount > 0:
        p = random.randint(0, len_program) * 4 + min_addr
        if p in program and len(program[p]) == 1:
            a = random.randint(1, max_amount)
            program[p] = [DARMInstruction(r) for r in corrupt_bits(31, 0, a, program[p][0].encoding)]
            corrupted_amount -= 1



def corrupt_instruction(program, original_instruction, address,
                        conditional=True, registers=False, opcode=False, amount=2):
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

