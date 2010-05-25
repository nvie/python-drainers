import unittest
from drainers import BufferedDrainer

class TestBufferedDrainer(unittest.TestCase):

    def setUp(self):
        self.callback_invoked = 0
        self.chunks = []

    def tearDown(self):
        # Set free memory
        self.callback_invoked = None
        self.chunks = None

    def collect(self, lines):
        self.callback_invoked += 1
        self.chunks.append(lines)

    def testVanillaBufferedDrainer(self):
        b = BufferedDrainer(['cat', 'fixtures/lipsum.txt'],
                            read_event_cb=self.collect)
        b.start()

        self.assertEquals(self.callback_invoked, 261)
        self.assertEquals(len(self.chunks), 261)
        for chunk in self.chunks:
            self.assertEquals(len(chunk), 1)

    def testChunkSize20(self):
        b = BufferedDrainer(['cat', 'fixtures/lipsum.txt'], read_event_cb=self.collect, chunk_size=20)
        b.start()

        # lipsum.txt contains 261 lines, so we expect:
        # 13 chunks of 20 lines
        # 1 chunk of 1 line
        self.assertEquals(self.callback_invoked, 14)
        self.assertEquals(len(self.chunks[:-1]), 13)
        for chunk in self.chunks[:-1]:
            self.assertEquals(len(chunk), 20)
        self.assertEquals(len(chunk), 20)
