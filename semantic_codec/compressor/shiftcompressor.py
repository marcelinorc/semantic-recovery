import struct
from math import fmod

from bitarray import bitarray

from semantic_codec.architecture.bits import Bits, BitQueue

class BitCompressor(object):

    def __init__(self, remove_bits, data, default_shift_count=2):
        self._shift_count = default_shift_count
        self._remove_bits = [x for x in remove_bits]
        self._remove_bits.sort(key=lambda x: x[0] * 10000 + x[1])
        self._data = data
        self.compressed_buffer = None



class ShiftCompressor(BitCompressor):
    """
    This class receives an interleaving list. Then it removes all the corrupted bits and shift the whole data
    to fit the missing bits.

    Dunno how efficient is the implementation, it uses bitarray. Certainly it was the fastest thing to implement
    """
    def __init__(self, remove_bits, data, default_shift_count=2):
        super(ShiftCompressor, self).__init__(remove_bits, data, default_shift_count)

    def compress(self):
        buf = struct.pack('%sI' % len(self._data), *self._data)
        a = bitarray(endian='big')
        a.frombytes(buf)
        for i in range(len(self._remove_bits) - 1, 0, -1):
            r = self._remove_bits[i]
            k = r[0] * BitQueue.WORD_SIZE + r[1]
            del a[k:k + self._shift_count]

        self.compressed_buffer = a.tobytes()


class SwapCompressor(BitCompressor):
    """
    This class receives an interleaving list. Then it removes all the corrupted bits and shift the whole data
    to fit the missing bits.

    Dunno how efficient is the implementation, it uses bitarray. Certainly it was the fastest thing to implement
    """

    def __init__(self, remove_bits, data, default_shift_count=2):
        super(SwapCompressor, self).__init__(remove_bits, data, default_shift_count)

    def compress(self):
        buf = struct.pack('%sI' % len(self._data), *self._data)
        a = bitarray(endian='big')
        a.frombytes(buf)
        for i in range(len(self._remove_bits) - 1, 0, -1):
            r = self._remove_bits[i]
            if len(r) > 2:
                continue
            k = r[0] * BitQueue.WORD_SIZE + r[1]
            if k >= len(a):
                continue
            for i in range(len(a) - self._shift_count, len(a)):
                    a[k] = 0
                    # k += 1
                    # a[k] = a[i]
                    # k += 1
            #del a[-self._shift_count:]

        self.compressed_buffer = a.tobytes()