
class ElfFunction(object):
    """
    Represents a function from the elf file
    """

    def __init__(self, name='unknwon'):
        self.name = name
        self.instructions = []

    def start_addr(self):
        if len(self.instructions) > 0:
            return self.instructions[0].address
        else:
            return 0

    def final_addr(self):
        if len(self.instructions) > 0:
            return self.instructions[0].address + self.length_in_bytes() - 4
        else:
            return 0

    def length_in_bytes(self):
        return len(self.instructions) * 4

    def __str__(self):
        return self.name