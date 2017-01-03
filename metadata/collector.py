from metadata.analysis import SSAFormBuilder
from metadata.darm_instruction import DARMInstruction


class MetadataCollector(object):

    """
    Collector of all metadata used in recovery semantics
    """
    def __init__(self):
        self._register_count = {}
        self._condition_count = {}
        self._instruction_count = {}
        self.empty_spaces = []

    @property
    def register_count(self):
        return self._register_count

    @property
    def condition_count(self):
        return self._condition_count

    @property
    def instruction_count(self):
        return self._instruction_count



    @staticmethod
    def _inc_key(d, key):
        d[key] = d[key] + 1 if key in d else 1

    @staticmethod
    def _inc_keys(d, keys):
        for k in keys:
            d[k] = d[k] + 1 if k in d else 1

    def collect(self, instructions):
        """
        Collects a series of metadata from an arm assemby program
        :param encodings:
        :return:
        """
        self.empty_spaces = []

        # Lazy me
        encodings = []

        for inst in instructions:
            if inst.encoding not in encodings:
                encodings.append(inst.encoding)
                self.empty_spaces.append(inst)
            self._inc_key(self._condition_count, inst.conditional_field)
            self._inc_key(self._instruction_count, inst.opcode_field)
            self._inc_keys(self._register_count, inst.registers_used())

        self.empty_spaces.sort(key=lambda x: x.encoding, reverse=True)





