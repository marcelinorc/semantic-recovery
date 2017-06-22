import os
from math import ceil
from unittest import TestCase
from os import listdir
from os.path import isfile, join

from semantic_codec.architecture.bits import Bits
from semantic_codec.interleaver.interleaver2d import *

class TestInterleave2D(TestCase):
    PRGMS_PATH = os.path.join(os.path.dirname(__file__), 'data/programs/')
    HELLOWORLD_PATH = os.path.join(os.path.dirname(__file__), 'data/programs/helloworld.bin')

    def test_sp(self):
        m = sucesive_packing(2)
        self.assertEqual(0.0, m[0, 0])
        self.assertEqual(5.0, m[3, 3])
        self.assertEqual(14.0, m[1, 2])
        self.assertEqual(15.0, m[3, 0])

        m = sucesive_packing(3)
        self.assertEqual(0.0, m[0, 0])
        self.assertEqual(21.0, m[7, 7])
        self.assertEqual(28.0, m[3, 1])
        self.assertEqual(11.0, m[4, 2])
        self.assertEqual(54.0, m[3, 6])

    def test_build_interleave_map_2d(self):
        r = build_2d_interleave_sp(241)
        self.assertEqual(0.0, r[0][0])
        self.assertEqual(240.0, r[6][0])
        self.assertEqual(26.0, r[7][7])

    def test_build_interleave_map_2d_flat(self):
        r = build_2d_interleave_sp(241, flat=True)
        for i in range(0, len(r)):
            self.assertGreater(241, i)  # There is no
            self.assertTrue(i in r, '{} not in r'.format(i))

    def test_interleave(self):
        """
        Test the interleaving
        """
        data = [3, 4, 8, 3, 5, 1, 1, 4, 9, 0, 4, 6, 2, 0, 1, 4]
        m = [int(k) for k in build_2d_interleave_sp(16, flat=True)]
        print(m)
        d = interleave(data, m, 2)
        self.assertEqual(1079132452, d[8].get_bytes()[0])
        self.assertEqual(310449603, d[0].get_bytes()[0])

    def do_interleave_deinterleave(self, data, packet_count, remove_packets = [], expected_errors = []):
        """
        Performs an interleave and deinterleave of a data removing certain packages.
        Then it perform some tests
        :param data: Data to send
        :param packet_count: Number of packets to sent
        :param remove_packets: Packets 'lost'
        """

        bits_per_interlave = 2
        WORD_SIZE = BitQueue.WORD_SIZE

        # Build the 2D interleave order
        m = build_2d_interleave_sp(packet_count, flat=True)

        # Interleave the data using the computed interleaving order
        d = interleave(data, m, bits_per_interlave)

        # Remove lost packets from the interleaved data
        for r in remove_packets:
            del d[r]

        # Deinterleave the data
        deintdata, errors = deinterleave(d, m, bits_per_interlave)

        if len(remove_packets) == 0:
            # If no package is lost, then the data should be perfect
            for k in range(0, len(data)):
                self.assertEqual(deintdata[k], data[k])
        else:
            # Compare some manually computed errors against the implementation
            for e in expected_errors:
                self.assertTrue(e in errors)

            # The following code works, but I realized is too complex for a test.
            # =============================================================================================
            # 1. For each packet lost there must be a series of corresponding errors signaled

            # A packet losses a series of bits periodically with a given jump distance
            #jump = bits_per_interlave * packet_count

            # Compute the total amount of bits in the data
            #total_bits = len(data) * BitQueue.WORD_SIZE

            # Compute the starting index for each packet in the remove packet list
            #b = [bits_per_interlave * m.index(p) for p in remove_packets]

            # Check that all errors were properly reported
            #while b[0] < total_bits:
            #    for i in range(0, len(b)):
            #        if b[i] < total_bits:
            #            t = (int(floor(b[i] / WORD_SIZE)), int(fmod(b[i], WORD_SIZE)))
            #            self.assertTrue(t in errors)
            #            errors.remove(t)
            #        # Jump to the next cyclic error
            #        b[i] += jump

            # =============================================================================================

            # On the other hand, for each error reported, there must be a corresponding error packet
            #self.assertEqual(0, len(errors))

    def test_interleave_deinterleave(self):
        """
        Test deinterleaving with a 'nice' number of packages
        """
        self.do_interleave_deinterleave([3, 4, 8, 3, 5, 1, 1, 4, 9, 0, 4, 6, 2, 0, 1, 4], 16)

    def test_interleave_deinterleave_multiple_size_matrix(self):
        """
        Test deinterleaving with an 'ugly' number of packages (7)
        """
        self.do_interleave_deinterleave([3, 4, 8, 3, 5, 1, 1, 4, 9, 0, 4, 6, 2, 0, 1, 4], 7)

    def test_interleave_deinterleave_programs(self):
        """
        Test to interleave and deinverleave and actual piece of program
        """
        data = open(TestInterleave2D.HELLOWORLD_PATH, "rb").read()
        packets = ceil(len(data) / 127)
        self.do_interleave_deinterleave(data, packets)

    def test_interleave_with_lost_packets(self):
        """
        Test the interleaving when some packets are removed from the stream
        """
        #data = open(TestInterleave2D.HELLOWORLD_PATH, "rb").read()
        #packets = ceil(len(data) / 127)

        # Some errors expected for this data, and lost packets
        expected_errors = [(0, 4), (0, 10), (0, 16), (10, 4), (10, 10), (10, 16), (14, 16), (15, 4), (15, 10)]

        self.do_interleave_deinterleave([3, 4, 8, 3, 5, 1, 1, 4, 9, 0, 4, 6, 2, 0, 1, 4],
                                        16, [2, 3, 4], expected_errors)
