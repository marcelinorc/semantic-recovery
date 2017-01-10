
class Bits(object):
    """
    Bit manipulation class for 32 bit numbers.

    Bits are represented from 0 to 31
    """

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
        if lower < 0 or higher >= 32:
            raise RuntimeError("Invalid range")
        return (2 ** (higher + 1) - 1) ^ (2 ** lower - 1)

    @staticmethod
    def on(value):
        """Returns a 2^value"""
        return 2 ** value