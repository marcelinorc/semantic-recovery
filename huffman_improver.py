"""
Scripts that takes a program and tries to improve the frequency of symbols to
obtain smaller huffman encodings values improves
"""
import os

import collections

from semantic_codec.architecture.capstone_instruction import CAPSInstruction
from semantic_codec.architecture.disassembler_readers import ElfioTextDisassembleReader
from semantic_codec.architecture.instruction_modifier import InstructionModifier
from semantic_codec.compressor.huffman import huffman_size
from semantic_codec.distributed.qos_functions import MockQoSFunction


def freq_info(x):
    """
    Obtains the frequency of fields in an instruction and the instructions where these fields were found
    :param x: A lambda to obtain the function in the function
    """

    # Frequency info
    freq = {}
    # Instructions containing the element being counted
    instructions_with = {}

    for p in program:
        c = collections.Counter(x(p))
        for k, r in c.items():
            if k not in instructions_with:
                instructions_with[k] = [p]
            elif p not in instructions_with[k]:
                instructions_with[k].append(p)

            if k not in freq:
                freq[k] = 0
            freq[k] += r

    keys_sorted = list(freq.keys())
    keys_sorted.sort(key=lambda k: freq[k])

    return freq, instructions_with, keys_sorted


ARM_SIMPLE = os.path.join(os.path.dirname(__file__), 'tests/data/basicmath_small.disam')
program = ElfioTextDisassembleReader(ARM_SIMPLE).read_instructions()

# Step 1. Find the frequency of registers in the program and the instructions containing those registers
reg_freq_counter, reg_with, reg_sorted = freq_info(lambda x: x.registers_used())

# Step 2. Find the frequency of opcodes in the program and the instructions containing that opcode
opcode_freq_counter, opcode_with, opcode_sorted = freq_info(lambda x: [x.opcode_field])

# Step 3. Find the frequency of opcodes in the program and the instructions containing those conditionals
cond_freq_counter, cond_with, cond_sorted = freq_info(lambda x: [x.conditional_field])

print('Original Huffman size Registers:    {}'.format(huffman_size(reg_freq_counter)))
print('Original Huffman size Opcodes:      {}'.format(huffman_size(opcode_freq_counter)))
print('Original Huffman size Conditionals: {}'.format(huffman_size(cond_freq_counter)))



# The QoS function that will determine if the change produces a correct program or not
qos = MockQoSFunction()

insmod = InstructionModifier()

# Try to change the registers
for register in range(0, len(reg_sorted)):
    for instruction in reg_with[reg_sorted[register]]:
        correct = False
        index = len(reg_sorted) - 1
        while not correct and index > register:
            new_reg = reg_sorted[index]
            # Change the address
            new_enc = insmod.modify_register(instruction.encoding, register, new_reg)
            qos.run(new_enc, instruction.address)
            index -= 1

#print(reg_freq_counter)
#print(opcode_freq_counter)
#print(cond_freq_counter)