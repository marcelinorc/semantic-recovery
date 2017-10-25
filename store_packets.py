"""
Program to store packets into a file
"""

import os
import struct
import sys

from bitarray import bitarray

from semantic_codec.architecture.disassembler_readers import ElfioTextDisassembleReader
from semantic_codec.compressor.shiftcompressor import ShiftCompressor, SwapCompressor
from semantic_codec.corruption.corruption import predict_corruption
from semantic_codec.interleaver.interleaver2d import *
from semantic_codec.metadata.probabilistic_rules.rules import from_functions_to_list_and_addr


if __name__ == '__main__':

    # Check Arguments
    expected_num_args = 3
    if len(sys.argv) != expected_num_args:
        print('Usage: <source_file> <output_file>')
        exit(1)

    # Read the file to be stored without the loss packets
    input_file = os.path.realpath(os.path.join(os.getcwd(), sys.argv[1]))
    try:
        f = open(input_file)
    except:
        print('Unable to find source: {}'.format(input_file))
        exit(1)
    # Parse the dissasembly text
    try:
        original_program = ElfioTextDisassembleReader(input_file).read_functions()
        original_program, fns = from_functions_to_list_and_addr(original_program)
        original_program = [inst.encoding for inst in original_program]
    except:
        print('Unable to parse source file, is it a valid dissasembly?')
        exit(1)

    # Interleave the file using the SP algorithm
    bits_per_interlave = 2
    packet_size = 16
    packet_count = len(original_program) * 4 / packet_size  # <- Total bytes in data divided by packet_size

    # Build the 2D interleave order
    m = build_2d_interleave_sp(packet_count, flat=True)

    # Predict up to 20% if corrupted bytes
    packet_lost = list(range(floor(packet_count / 5)))
    errors = predict_corruption(packet_count, bits_per_interlave, len(original_program) * 4, m, packet_lost)

    # Remove up to 20 percent of packets
    compressor = SwapCompressor(errors, original_program)
    compressor.compress()

    # Store the remaining
    output_file = os.path.realpath(os.path.join(os.getcwd(), sys.argv[2]))
    fout = open(output_file, 'wb')
    fout.write(compressor.compressed_buffer)
    fout.close()

    # Store the remaining
    output_file = os.path.realpath(os.path.join(os.getcwd(), sys.argv[2])) + 'a100'
    fout = open(output_file, 'wb')
    buf = struct.pack('%sI' % len(original_program), *original_program)
    a = bitarray(endian='big')
    a.frombytes(buf)
    b = a.tobytes()
    fout.write(b)
    fout.close()
