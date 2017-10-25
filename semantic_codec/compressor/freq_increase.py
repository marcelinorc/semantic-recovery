
class FrequencyIncreaser(object):
    """
    Increases the frequency of a given instruction part in the instructions of a given list.
    """

    def __init__(self):
        self._program = None

    @property
    def program(self):
        return self._program

    @program.setter
    def program(self, program):
        self._program = program

    def incr_registers(self):
        """
        Increases the frequency of most frequent registers and decreases frequency of least common registers
        :return:
        """
        pass

    def incr_cond(self):
        """
        Increases the frequency of most frequent registers and decreases frequency of least common registers
        :return:
        """
        pass

    def incr_operand(self):
        """
        Increases the frequency of most frequent registers and decreases frequency of least common registers
        :return:
        """
        pass
