from unittest import TestCase

from semantic_codec.architecture.bits import BitQueue


class TestBitQueue(TestCase):

    def enqueue_dequeue(self, word):
        # Let's que and deque these two numbers into two BitQueues.
        # They form a nice pattern in binary
        a = 3435956360
        b = 4272458479

        br = 0
        ar = 0

        q1 = BitQueue(word)
        q2 = BitQueue(word)

        for i in range(0, 32, word * 2):
            q1.enqueue(a, i)
            q2.enqueue(b, i)
            if i + word < 32:
                q1.enqueue(b, i + word)
                q2.enqueue(a, i + word)

        i = 0
        while i < 32 and not q1.empty():
            ar = q1.dequeue(ar, i)
            br = q2.dequeue(br, i)
            i += word
            if i < 32 and not q1.empty():
                br = q1.dequeue(br, i)
                ar = q2.dequeue(ar, i)
                i += word

        self.assertEqual(a, ar)
        self.assertEqual(b, br)

    def test_enqueue_dequeue_w7(self):
        self.enqueue_dequeue(7)

    def test_enqueue_dequeue_w2(self):
        self.enqueue_dequeue(2)

    def test_enqueue_dequeue_w1(self):
        self.enqueue_dequeue(1)
