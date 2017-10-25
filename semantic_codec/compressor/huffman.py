from heapq import heappush, heappop, heapify
from collections import defaultdict

import collections


def encode(symb2freq):
    """Huffman encode the given dict mapping symbols to weights"""
    heap = [[wt, [sym, ""]] for sym, wt in symb2freq.items()]
    heapify(heap)
    while len(heap) > 1:
        lo = heappop(heap)
        hi = heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
    return sorted(heappop(heap)[1:], key=lambda p: (len(p[-1]), p))


def huffman_size(symb_freq, huff=None):
    if not huff:
        huff = encode(symb_freq)
    size = 0
    for p in huff:
        size += symb_freq[p[0]] * len(p[1])
    return size


def huffman_test(txt):
    symb2freq = collections.Counter(txt)
    huff = encode(symb2freq)
    size = 0
    print("Symbol\tWeight\tHuffman Code")
    for p in huff:
        size += symb2freq[p[0]] * len(p[1])
        print("%s\t%s\t%s" % (p[0], symb2freq[p[0]], p[1]))
    print('Msg Size is {}'.format(size))

#huffman_test("this is an example for huffman encoding")
#huffman_test("thas as an axampla for haffman ancoding")
