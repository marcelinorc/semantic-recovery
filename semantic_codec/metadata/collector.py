from semantic_codec.architecture.arm_instruction import AReg


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
        """
        self.empty_spaces = []

        # Lazy me
        encodings = []

        dist = [0] * 18
        defined = [False] * 18
        storage_mean_dist = {}

        for inst in instructions:
            if inst.is_undefined:
                continue
            if inst.encoding not in encodings:
                encodings.append(inst.encoding)
                self.empty_spaces.append(inst)
            self._inc_key(self._condition_count, inst.conditional_field)
            self._inc_key(self._instruction_count, inst.opcode_field)
            self._inc_keys(self._storage_count, inst.storages_used())

            read = inst.storages_read()
            for s in range(0, AReg.STORAGE_COUNT) :
                if defined[s]:
                    if s in read:
                        if s not in storage_mean_dist:
                            self._storage_min_dist[s] = dist[s]
                            self._storage_max_dist[s] = dist[s]
                            # The numbers of times here is different that the number of times a storage is read
                            # as it can be read several times per instruction
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

            # Count the distances between write and read of storages
            for s in inst.storages_written():
                defined[s] = True
                dist[s] = 0

        # Compute the mean distance between a register being read and a register being written
        for k in storage_mean_dist:
            d, t = storage_mean_dist[k]
            self._storage_mean_dist[k] = d / t

        # Comput the empty spaces in the encoding
        self.empty_spaces.sort(key=lambda x: x.encoding, reverse=True)





