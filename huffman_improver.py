"""
Scripts that takes a program and tries to improve the frequency of symbols to
obtain smaller huffman encodings values improves
"""
import os

import collections

from semantic_codec.architecture.capstone_instruction import CAPSInstruction
from semantic_codec.architecture.disassembler_readers import ElfioTextDisassembleReader
from semantic_codec.architecture.instruction_modifier import InstructionModifier
from semantic_codec.compressor.huffman import huffman_size, InstructionPartFrequencyCounter, \
    InstructionPartFrequencyChanger
from semantic_codec.distributed.qos_functions import MockQoSFunction






ARM_SIMPLE = os.path.join(os.path.dirname(__file__), 'tests/data/basicmath_small.disam')
program = ElfioTextDisassembleReader(ARM_SIMPLE).read_instructions()
fc = InstructionPartFrequencyCounter()
fc.count(program)

# Print Before
print('Original Huffman size Registers:    {}'.format(huffman_size(fc.reg_frequency)))
print('Original Huffman size Opcodes:      {}'.format(huffman_size(fc.opcode_frequency)))
print('Original Huffman size Conditionals: {}'.format(huffman_size(fc.cond_frequency)))



# The QoS function that will determine if the change produces a correct program or not
qos = MockQoSFunction()
changer = InstructionPartFrequencyChanger(program, qos, fc)
# Try to change the registers
changer.change_registers()

# Print after
print('Original Huffman size Registers:    {}'.format(huffman_size(fc.reg_frequency)))
