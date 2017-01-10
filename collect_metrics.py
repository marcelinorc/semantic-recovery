import os
from semantic_codec.architecture.disassembler_readers import TextDisassembleReader
from semantic_codec.metadata.collector import MetadataCollector

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

filename = os.path.join(os.path.dirname(__file__), 'tests/data/helloworld.armasm')
fns = TextDisassembleReader(filename).read_functions()

def collect_and_print(fun_name, instructions, program):
    c = MetadataCollector()
    print("Function: " + fun_name)
    c.collect(instructions)
    print(c.condition_count)
    print(c.instruction_count)
    print(c.register_count)
    prev_inst = None
    for inst in c.empty_spaces:
        if prev_inst is None:
            print('{}; 0; {}'.format(inst.encoding, inst))
        else:
            print('{}; {}; {}'.format(inst.encoding, abs(prev_inst.encoding - inst.encoding), inst))
        prev_inst = inst

    x = [0 if i not in c.register_count else c.register_count[i] for i in range(0, 18)]
    ind = np.arange(18)
    plt.clf()
    plt.bar(ind, x, 0.35)
    plt.tight_layout()
    plt.savefig(program + '_registers.png')

    x = [0 if i not in c.condition_count else c.condition_count[i] for i in range(0, 15)]
    ind = np.arange(15)
    plt.clf()
    plt.bar(ind, x, 0.35)
    plt.tight_layout()
    plt.savefig(program + '_condition.png')

    x = [0 if i not in c.instruction_count else c.instruction_count[i] for i in range(0, 200)]
    ind = np.arange(200)
    plt.clf()
    plt.bar(ind, x, 0.35)
    plt.tight_layout()
    plt.savefig(program + '_instruction.png')
    plt.show()

#print("===========================")
#print("=======FUNCTION WISE=======")
#print("===========================")
#for key, instructions in fns.items():
#    collect_and_print(key, instructions)

print("===========================")
print("=======GlOBAL       =======")
print("===========================")
instructions = TextDisassembleReader(filename).read()
collect_and_print("global", instructions, "helloworld")



