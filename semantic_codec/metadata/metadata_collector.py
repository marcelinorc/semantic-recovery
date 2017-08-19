from semantic_codec.architecture.arm_constants import AReg


def _inc_key(d, key):
    d[key] = d[key] + 1 if key in d else 1


def _inc_keys(d, keys):
    for k in keys:
        d[k] = d[k] + 1 if k in d else 1


class MetadataCollector(object):
    """
    Collector of all metadata used in recovery semantics
    """

    def __init__(self):
        self._storage_count = {}
        self._condition_count = {}
        self._instruction_count = {}
        self._storage_min_dist = {}
        self._storage_max_dist = {}
        self._storage_mean_dist = {}
        self.empty_spaces = []

    @property
    def storage_min_dist(self):
        return self._storage_min_dist

    @property
    def storage_max_dist(self):
        return self._storage_max_dist

    @property
    def storage_mean_dist(self):
        return self._storage_mean_dist

    @property
    def storage_count(self):
        return self._storage_count

    @property
    def condition_count(self):
        return self._condition_count

    @property
    def instruction_count(self):
        return self._instruction_count

    def collect(self, instructions):
        """
        Collects a series of metadata from an arm assembly program
        """

        # TODO: Collect the number of instructions writing to no register

        self.empty_spaces = []

        # Lazy me
        encodings = []

        dist = [0] * 18
        defined = [False] * 18
        storage_mean_dist = {}

        for inst in instructions:
            if inst.ignore:
                continue
            if inst.encoding not in encodings:
                encodings.append(inst.encoding)
                self.empty_spaces.append(inst)
            _inc_key(self._condition_count, inst.conditional_field)
            _inc_key(self._instruction_count, inst.opcode_field)
            _inc_keys(self._storage_count, inst.storages_used())

            read = inst.storages_read()
            for s in range(0, AReg.STORAGE_COUNT):
                if defined[s]:
                    if s in read:
                        if s not in storage_mean_dist:
                            self._storage_min_dist[s] = dist[s]
                            self._storage_max_dist[s] = dist[s]
                            # The numbers of times here is different that the number of times a storage is read_instructions
                            # as it can be read_instructions several times per instruction
                            storage_mean_dist[s] = (dist[s], 1)
                        else:
                            if self._storage_min_dist[s] > dist[s]:
                                self._storage_min_dist[s] = dist[s]
                            if self._storage_max_dist[s] < dist[s]:
                                self._storage_max_dist[s] = dist[s]
                            d, t = storage_mean_dist[s]
                            storage_mean_dist[s] = (d + dist[s], t + 1)
                        defined[s] = False
                        dist[s] = 0
                    else:
                        dist[s] += 1

            # Count the distances between write and read_instructions of storages
            for s in inst.storages_written():
                defined[s] = True
                dist[s] = 0

        # Compute the mean distance between a register being read_instructions and a register being written
        for k in storage_mean_dist:
            d, t = storage_mean_dist[k]
            self._storage_mean_dist[k] = d / t

        # Comput the empty spaces in the encoding
        self.empty_spaces.sort(key=lambda x: x.encoding, reverse=True)


class CorruptedProgramMetadataCollector(object):
    def __init__(self):
        # Number of address having at least one candidate with a given conditional
        self.address_with_cond = {}
        # Number of address having at least one candidate with a given opcode
        self.address_with_op = {}
        # Number of address having at least one candidate with a given register
        self.address_with_reg = {}

    def collect(self, program):

        self.address_with_cond = {}
        self.address_with_op = {}
        self.address_with_reg = {}

        for addr in program:
            cond, op, reg = {}, {}, {}
            for inst in program[addr]:
                if inst.ignore:
                    continue
                cond[inst.conditional_field] = 1
                op[inst.opcode_field] = 1
                for s in inst.storages_used():
                    reg[s] = 1
            for k in cond.keys():
                _inc_key(self.address_with_cond, k)
            for k in op.keys():
                _inc_key(self.address_with_op, k)
            for k in reg.keys():
                _inc_key(self.address_with_reg, k)

            pass
