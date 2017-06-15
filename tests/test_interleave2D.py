from unittest import TestCase

from semantic_codec.interleaver.interleaver2d import sucesive_packing, build_2d_interleave_sp, interleave, deinterleave


class TestInterleave2D(TestCase):

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

    def test_build_interleave_map_2D_flat(self):
        r = build_2d_interleave_sp(241, flat=True)
        for i in range(0, len(r)):
            self.assertGreater(241, i) # There is no
            self.assertTrue(i in r, '{} not in r'.format(i))

    def test_interleave(self):
        # Generate message. Just a bunch of random numbers
        data = [3, 4, 8, 3, 5, 1, 1, 4, 9, 0, 4, 6, 2, 0, 1, 4]
        m = [int(k) for k in build_2d_interleave_sp(16, flat=True)]
        print(m)
        d = interleave(data, m, 2)
        self.assertEqual(1079132452, d[8].get_bytes()[0])
        self.assertEqual(310449603, d[0].get_bytes()[0])

    def test_interleave_deinterleave(self):
        # Generate message. Just a bunch of random numbers
        data = [3, 4, 8, 3, 5, 1, 1, 4, 9, 0, 4, 6, 2, 0, 1, 4]
        m = build_2d_interleave_sp(16, flat=True)
        print(m)

        d = interleave(data, m, 2)

        deint = deinterleave(d, m, 2)

        for k in range(0, len(data)):
            self.assertEqual(deint[0][k], data[k])

    def test_interleave_deinterleave_multiple_size_matrix(self):
        # Generate message. Just a bunch of random numbers
        data = [3, 4, 8, 3, 5, 1, 1, 4, 9, 0, 4, 6, 2, 0, 1, 4]
        m = build_2d_interleave_sp(7, flat=True)
        print(m)

        d = interleave(data, m, 2)

        deint = deinterleave(d, m, 2)

        for k in range(0, len(data)):
            self.assertEqual(deint[0][k], data[k])


    def test_interleave_deinterleave_a_program(self):
        self.fail()