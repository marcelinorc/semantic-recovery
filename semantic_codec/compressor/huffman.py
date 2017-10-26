from heapq import heappush, heappop, heapify
from collections import defaultdict

import collections

from semantic_codec.architecture.instruction_modifier import InstructionModifier


class InstructionPartFrequencyChanger(object):
    def __init__(self, program, quality_of_service, counter):
        self._program = program
        self._qos = quality_of_service
        self._counter = counter

    def _init_counter(self):
        if not self._counter:
            self._counter = InstructionPartFrequencyCounter()
            self._counter.count(self._program)

    def change_registers(self):
        insmod = InstructionModifier()
        self._init_counter()
        self._change_parts(insmod.modify_register,
                           self._counter.reg_with,
                           self._counter.reg_frequency)

    def _change_parts(self, changer, with_part, frequency):
        """
        Change some part of the instruction to increase its frequency
        :param changer: method to change the instruction part
        :param next:  Function that tells if more parts of that type remains
        :param with_part: Instruction containing that part
        :param frequency: Frequency dictionary
        :param qos: Quality of Service function
        """

        qos = self._qos

        freq_sorted = list(frequency.keys())
        freq_sorted.sort(key=lambda k: frequency[k])

        # Go through all registers, from least frequent to more frequent
        for i in range(0, len(freq_sorted)):

            part = freq_sorted[i]

            # For all instructions containing this register
            for instruction in with_part[part]:

                # Try to change the register with a more frequent one, starting with the most frequent
                index = len(freq_sorted) - 1

                # Flag to indicate that at least a register was correctly changed
                any_correct = False

                while not any_correct and index > part:
                    # New, most frequent register
                    new_part = freq_sorted[index]

                    # Now try to change any infrequent register from the instruction.
                    # There could be more than one use of the register
                    # So try them all
                    has_next = True
                    while has_next:

                        # Change the address
                        # Using the instruction modifier
                        new_enc, has_next = changer(instruction, part, new_part)

                        # Run the program and check if it works
                        correct_qos = qos.run(new_enc, instruction.address)

                        any_correct = any_correct or correct_qos

                        # If it is correct, update the frequency dictionary
                        if correct_qos:
                            if part in frequency:
                                frequency[part] -= 1


                    # The most frequent register was no good, try next one
                    if not any_correct:
                        index -= 1


class InstructionPartFrequencyCounter(object):
    """
    Class that counts the frequency of instructions parts in a program
    """

    def __init__(self):
        self.reg_frequency = None
        self.reg_with = None
        self.reg_sorted = None
        self.opcode_frequency = None
        self.opcode_with = None
        self.opcode_sorted = None
        self.cond_frequency = None
        self.cond_with = None
        self.cond_sorted = None

    def freq_info(self, program, x):
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

        return freq, instructions_with

    def count(self, program):
        # Step 1. Find the frequency of registers in the program and the instructions containing those registers
        self.reg_frequency, self.reg_with = self.freq_info(program, lambda x: x.registers_used())
        # Step 2. Find the frequency of opcodes in the program and the instructions containing that opcode
        self.opcode_frequency, self.opcode_with = self.freq_info(program, lambda x: [x.opcode_field])
        # Step 3. Find the frequency of opcodes in the program and the instructions containing those conditionals
        self.cond_frequency, self.cond_with = self.freq_info(program, lambda x: [x.conditional_field])


def encode(symb2freq):
    """Huffman encode the given dict mapping symbols to weights"""
    heap = [[wt, [sym, ""]] for sym, wt in symb2freq.items()]
    heapify(heap)
    while len(heap) > 1:
        lo = heappop(heap)
        hi = heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
    return sorted(heappop(heap)[1:], key=lambda p: (len(p[-1]), p))


def huffman_size(symb_freq, huff=None):
    if not huff:
        huff = encode(symb_freq)
    size = 0
    for p in huff:
        size += symb_freq[p[0]] * len(p[1])
    return size


def huffman_test(txt):
    symb2freq = collections.Counter(txt)
    huff = encode(symb2freq)
    size = 0
    print("Symbol\tWeight\tHuffman Code")
    for p in huff:
        size += symb2freq[p[0]] * len(p[1])
        print("%s\t%s\t%s" % (p[0], symb2freq[p[0]], p[1]))
    print('Msg Size is {}'.format(size))

# huffman_test("this is an example for huffman encoding")
# huffman_test("thas as an axampla for haffman ancoding")
