from math import sqrt, fmod, floor, log
import numpy

from semantic_codec.architecture.bits import BitQueue


def sucesive_packing(m):
    """
    Performs the sucesive packing algorithm in a matrix. Which creates a 4^m X 4 ^m matrix of interleaved numbers
    :param m: Exponent to create the matrix.
    :return:
    """

    if m <= 0:
        return [[0]]

    matrix = numpy.zeros(shape=(2 ** m, 2 ** m))

    matrix[0, 0] = 0
    matrix[0, 1] = 2
    matrix[1, 0] = 3
    matrix[1, 1] = 1

    for n in range(1, m):
        # Indexes
        w = 2 ** n

        # 4x + 2 quadrant (upper right)
        for i in range(w, w + w):
            for j in range(0, w):
                matrix[j, i] = int(matrix[j, i - w] * 4 + 2)

        # 4x + 3 (lower left)
        for i in range(0, w):
            for j in range(w, w + w):
                matrix[j, i] = int(matrix[j - w, i] * 4 + 3)

        # 4x + 1 (lower right)
        for i in range(w, w + w):
            for j in range(w, w + w):
                matrix[j, i] = int(matrix[j - w, i - w] * 4 + 1)

        # 4x quadrant (upper left)
        for i in range(0, w):
            for j in range(0, w):
                matrix[j, i] = int(4 * matrix[j, i])

    return matrix


def build_2d_interleave_sp(packets, flat=False):
    """
    Builds a 4^nx4^n matrix set for interleaving a 2D data. It uses the successive packing algorithm
    by Shi and Zhang described in "A new two-dimensional interleaving technique using successive packing"

    The SP algorithm works only with 4^nx4^n matrices. In order to fit data of any size into that, we
    build several matrices of size 4^n, 4^(n-1)... 4^0 and then we interleave them once more using a simple
    algorithm that goes through all matrices taking the mth row each time.

    :param packets: Number of packets to pack the data
    :param data_width: With of the data to be packet
    :return:
    """

    matrices = []
    current_package_index = 0

    # Distribute all packages in a given pattern
    while packets > 0:

        # Find a 4^m X 4^m such as 4^m is the closest power of 4 smaller than the packet size
        n = floor(log(packets, 4))
        matrix_size = int(2 ** n)
        # Compute the number of packets that fits in this matrix
        packets_in_matrix = 4 ** n

        # Build several matrix of this size
        matrix_count = floor(packets / packets_in_matrix)

        if matrix_count > 0:
            # Obtain the sucesive packing for a matrix of this size.
            m1 = sucesive_packing(n)
            for i in range(0, matrix_size):
                for j in range(0, matrix_size):
                    m1[i][j] += current_package_index

            # Since a matrix only fits 4^n packets, count how many packets we have allotted so far
            current_package_index += packets_in_matrix

            # Append the matrix to the set of matrices
            matrices.append(m1)

            # Then obtain other matrices of the same size.
            # Don't compute the same sucesive packing twice, just add the index to the first matrix obtained
            for k in range(0, matrix_count - 1):
                mi = numpy.zeros(shape=(2 ** n, 2 ** n))
                for i in range(0, matrix_size):
                    for j in range(0, matrix_size):
                        mi[i][j] = m1[i][j] + packets_in_matrix * (k + 1)
                current_package_index += packets_in_matrix
                matrices.append(mi)
        # Compute how many packets remain to be allotted
        packets = fmod(packets, packets_in_matrix * matrix_count)

    # Interleave matrixs rows between each others to increase interleave
    result = []
    for n in range(0, len(matrices[0][0])):
        for i in range(0, len(matrices)):
            if len(matrices[i]) > n:
                result.append(matrices[i][n])

    # Give the order as a flat list of numbers
    if flat:
        flat_result = []
        for r in result:
            flat_result.extend(r)
        return flat_result

    return result


def build_2d_interleave_matrix_blaum(message_size, packet_size, data_width=-1, data_height=-1):
    """
    Produces a 2D interleaved matrix based in the results described in
    'Interleaving Schemes for Multidimensional Cluster Errors' by Blaum, Bruck and Vardy
    as well in the results provided in https://oeis.org/A047838,
    which are further explained in https://oeis.org/A047838/a047838.txt.

    Example for t == 3.

    1. Create two matrices
     A          B
    1 2 3 |  9  10 11
    4 5 6 |  12 13 14
    7 8 9 |  15 16 17

    2. Create a checkboard with these matrices:
     A B
     B A

    3. Interleave columns and rows aiming at making the sum of the differences maximal

    :param packet_size: Size of the packet (the unit does not matter as long as is the same as the message_size)
    :param message_size: Size of the message (the unit does not matter as long as is the same as the packet_size)
    :param data_width: Width of the data measured in the amount of packets per row. (It is  2D data, so it has width)
    :param data_height: Height of the data measured in the amount of packets per column.
     """

    if data_width != -1 and data_height == -1:
        data_height = round(message_size / data_width)
    elif data_height != -1 and data_width == -1:
        data_width = round(message_size / data_height)
    elif data_height == -1 and data_width == -1:
        raise RuntimeError('Cannot infer both data with and height')

    m = round(message_size / packet_size)
    b = round(sqrt(2 * m - 1))

    return [[int(abs(fmod(x - y * b, m))) for x in range(data_width)] for y in range(data_height)]


def interleave(data, interleave_order, word_size=8):
    """
    Interleaves data given an interleave order
    :param data: Data to interleave
    :param matrix: Interleaving order
    :param word_size: Size of the chunk of data that is going to be interleaved. By default is 8 (a byte).
    :return: The data interleaved according to the interleave order
    """
    packets = {int(index): BitQueue(word_size) for index in interleave_order}

    bit_index = 0
    arr_index = 0
    k = 0
    while arr_index < len(data):
        pkt = packets[interleave_order[k]]
        pkt.enqueue(data[arr_index], bit_index)
        bit_index += word_size
        k = 0 if k == len(interleave_order) - 1 else k + 1
        if bit_index > 31 and arr_index < len(data):
            bit_index -= 32
            arr_index += 1

    return packets


def deinterleave(packets, interleave_order, word_size=8):

    """
    Deinterleaves the data. If a packet is missing, it adds this information to the error list.
    :param packets: Packets receive
    :param interleave_order: Order in which the packets are interleaved
    :param word_size: Size of the arrays word size
    :return: Data and the error list
    """
    k = len(interleave_order) - 1
    while k > -1 and packets[interleave_order[k]] is None:
        k -= 1

    last_queue = None
    if k == 0:
        raise RuntimeError('All packets are lost')
    else:
        last_queue = packets[interleave_order[k]]

    errors = []

    data = BitQueue(word_size)
    while not last_queue.empty():
        for p in interleave_order:
            a = 0
            if not p in packets or packets[p] is None:
                errors.append((data._eq_word, data._eq_bit))
            else:
                a = packets[p].dequeue(a, 0)
            data.enqueue(a, 0)

    return (data.get_bytes(), errors)

# for k in range(0, 3):
#    for i in range(0, n):
#        print("{} {} {} {} {} {}".format(matrix1[i], matrix2[i], matrix1[i], matrix2[i], matrix1[i], matrix2[i]))
#
# print("------")
#
# for i in range(0, n, 2):
#    for j in range(0, n, 2):
#        m = matrix1[i][j]
#        matrix1[i][j] = matrix2[i][j]
#        matrix2[i][j] = m
#
# for k in range(0, 3):
#    for i in range(0, n):
#        print("{} {} {} {} {} {}".format(matrix1[i], matrix2[i], matrix1[i], matrix2[i], matrix1[i], matrix2[i]))
#
# print("------")
#
# for i in range(0, n - 1, 2):
#    for j in range(0, n - 2):
#        m = matrix1[j][i]
#        matrix1[j][i] = matrix1[n - j - 1][i]
#        matrix1[n - j - 1][i] = m
#
#        m = matrix2[j][i]
#        matrix2[j][i] = matrix2[n - j - 1][i]
#        matrix2[n - j - 1][i] = m
#
# for k in range(0, 3):
#    for i in range(0, n):
#        print("{} {} {} {} {} {}".format(matrix1[i], matrix2[i], matrix1[i], matrix2[i], matrix1[i], matrix2[i]))
