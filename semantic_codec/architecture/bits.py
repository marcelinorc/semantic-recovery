class BitQueue(object):

    WORD_SIZE = 32

    def __init__(self, word_size = 1):
        self._bytes = [0]
        self._eq_word = 0
        self._eq_bit = 0
        self._dq_bit = 0
        self.word_size = word_size

    def enqueue(self, value, from_bit):
        """
        Take a number of bits equal to the word size from value into the bitstream
        :param value: Value to obtain the bits from
        :param from_bit: index of the bit to start copying bits
        """
        Bits.check_range(0, from_bit)

        if self._eq_bit + self.word_size - 1 > BitQueue.WORD_SIZE - 1:
            w = max(0, BitQueue.WORD_SIZE - self._eq_bit - 1)
            self._bytes[self._eq_word] = Bits.copy_bits(value, self._bytes[self._eq_word],
                                                        from_bit, from_bit + w, self._eq_bit)
            self._eq_word += 1
            self._bytes.append(0)

            w = max(0, self._eq_bit + self.word_size - BitQueue.WORD_SIZE - 1)
            self._eq_bit = 0
            self._bytes[self._eq_word] = Bits.copy_bits(value, self._bytes[self._eq_word],
                                                        from_bit, from_bit + w, self._eq_bit)
        else:
            w = max(0, from_bit + self.word_size - 1)
            self._bytes[self._eq_word] = Bits.copy_bits(value, self._bytes[self._eq_word],
                                                        from_bit, w, self._eq_bit)

        self._eq_bit += self.word_size
        if self._eq_bit > BitQueue.WORD_SIZE - 1:
            self._eq_bit -= BitQueue.WORD_SIZE
            self._eq_word += 1
            self._bytes.append(0)

    def empty(self):
        if self._eq_word < 0:
            return True
        elif self._eq_word == 0 and self._eq_bit <= self._dq_bit:
            return True
        return False

    def dequeue(self, value, to_bit):
        Bits.check_range(0, to_bit)

        if self._dq_bit + self.word_size - 1 > BitQueue.WORD_SIZE - 1:
            w = BitQueue.WORD_SIZE - self._dq_bit
            value = Bits.copy_bits(self._bytes[0], value, self._dq_bit, self._dq_bit + w - 1, to_bit)
            self._bytes.pop(0)
            self._eq_word -= 1

            w = self._dq_bit + self.word_size - BitQueue.WORD_SIZE
            self._dq_bit = 0
            value = Bits.copy_bits(self._bytes[0], value, self._dq_bit, self._dq_bit + w - 1, to_bit)
        else:
            w = self.word_size
            value = Bits.copy_bits(self._bytes[0], value, self._dq_bit, self._dq_bit + w - 1, to_bit)

        self._dq_bit += w
        if self._dq_bit > BitQueue.WORD_SIZE - 1:
            self._dq_bit -= BitQueue.WORD_SIZE
            self._bytes.pop(0)
            self._eq_word -= 1

        return value

    def get_bytes(self):
        return self._bytes


class Bits(object):
    """
    Bit manipulation class for 32 bit numbers.

    Bits are represented from 0 to 31
    """
    @staticmethod
    def check_range(lo, hi):
        if lo > hi:
            raise RuntimeError('Lower bit is in fact higher {} > {}'.format(lo, hi))
        if lo < 0 or hi >= 32:
            raise RuntimeError("Invalid range Lo: {} - Hi : {}".format(lo, hi))

    @staticmethod
    def copy_bits(value_from, value_to, src_from, src_to, dest_from):
        """
        Copy bits from one integer to other
        :param value_from: Integer copy from
        :param value_to: Integer to copy to
        :param src_from: Bit where the copy will start in the source
        :param src_to: Bit where the copy will stop in the source
        :param dest_from: Bit where the copy will start in the destination
        :return:
        """
        dest_to = dest_from + (src_to - src_from)
        Bits.check_range(src_from, src_to)
        Bits.check_range(dest_from, dest_to)

        mask = Bits.set(dest_to, dest_from)
        value_to &= ~ mask
        if src_from > dest_from:
            value_to |= mask & (value_from >> (src_from - dest_from))
        else:
            value_to |= mask & (value_from << (dest_from - src_from))

        return value_to

    @staticmethod
    def are_on(value, higher, lower):
        """
        Indicates if the n
        :param value:
        :param higher:
        :param lower:
        :param max:
        :return:
        """
        return value & Bits.set(higher, lower) != 0

    @staticmethod
    def is_on(value, bit):
        return value & (2**bit) != 0

    @staticmethod
    def set(higher, lower):
        Bits.check_range(lower, higher)
        return (2 ** (higher + 1) - 1) ^ (2 ** lower - 1)

    @staticmethod
    def on(value):
        """Returns a 2^value"""
        return 2 ** value