from os import listdir
from os.path import isfile, join

results_equals = '/media/elmarce/Windows/MarcelStuff/DATA/WSN/forgivingzones_study/basicmath_resultsequal.txt'

# Create a dict storing all equals
equals_dict = {}
with open(results_equals, "r") as myfile:
    for line in myfile:
        key, value = line.split(':')
        key = key.strip().split('.')[0]
        value = value.strip()
        equals_dict[key+'.disam'] = True if value == 'True' else False

disassembly_dir = '/home/elmarce/MarcelStuff/DATA/WSN/lossy-programs/dissasemble/mod_basicmath/'
mod_files = [f for f in listdir(disassembly_dir) if isfile(join(disassembly_dir, f))]

original_file = mod_files[0]
with open(disassembly_dir + original_file, "r") as myfile:
    originaldata = myfile.readlines()

total = len(mod_files)

for f in mod_files:
    diff = 0 # we are not using the original file
    if not equals_dict[f]:
        continue
    with open(disassembly_dir + f, "r") as myfile:
        k = 0
        for line in myfile:
            if originaldata[k] != line:
                diff += 1
                if diff > 1:
                    print("[{} - {}] : {} >>> {}".format(f, k, originaldata[k].strip(), line.strip()))
            k += 1
