import unittest
import traceback
from drainers import BufferedDrainer

class TestBufferedDrainer(unittest.TestCase):

    def setUp(self):
        self.callback_invoked = 0
        self.triggered_by_timer = 0
        self.triggered_by_chunk_size_exceeded = 0
        self.triggered_otherwise = 0
        self.chunks = []

    def tearDown(self):
        # Set free memory
        self.chunks = None

    def collect(self, lines):
        self.callback_invoked += 1
        self.chunks.append(lines)

        called_functions = [fname for _, _, fname, _ in traceback.extract_stack()]
        if '_flush_and_reset' in called_functions:
            self.triggered_by_timer += 1
        elif '_wrapper' in called_functions:
            self.triggered_by_chunk_size_exceeded += 1
        else:
            self.triggered_otherwise += 1

    def assertChunksCountUpTo30(self):
        i = 1
        for lines in self.chunks:
            for line, is_err in lines:
                self.assertFalse(is_err)
                self.assertEquals(int(line.strip()), i)
                i += 1

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

    def testTimerBasedBuffering(self):
        b = BufferedDrainer(['sh', 'fixtures/counter.sh'],
                            read_event_cb=self.collect,
                            flush_timeout=0.2)
        b.start()

        self.assertEquals(self.callback_invoked, 3)
        self.assertEquals(self.triggered_by_chunk_size_exceeded, 0)
        self.assertEquals(self.triggered_by_timer, 2)
        self.assertEquals(self.triggered_otherwise, 1)
        self.assertEquals(len(self.chunks), 3)
        for chunk in self.chunks:
            self.assertEquals(len(chunk), 10)
        self.assertChunksCountUpTo30()

    def testTimerBasedLargerTimeout(self):
        b = BufferedDrainer(['sh', 'fixtures/counter.sh'],
                            read_event_cb=self.collect,
                            flush_timeout=2.5)
        b.start()

        self.assertEquals(self.callback_invoked, 2)
        self.assertEquals(self.triggered_by_chunk_size_exceeded, 0)
        self.assertEquals(self.triggered_by_timer, 1)
        self.assertEquals(self.triggered_otherwise, 1)
        self.assertEquals(len(self.chunks), 2)
        self.assertChunksCountUpTo30()

    def testWhenCombinedLikeThisTheTimerNeverFires(self):
        b = BufferedDrainer(['sh', 'fixtures/counter.sh'],
                            read_event_cb=self.collect,
                            chunk_size=10,
                            flush_timeout=2.5)
        b.start()

        self.assertEquals(self.callback_invoked, 3)
        self.assertEquals(self.triggered_by_timer, 0)
        self.assertEquals(self.triggered_by_chunk_size_exceeded, 3)
        self.assertEquals(self.triggered_otherwise, 0)
        self.assertEquals(len(self.chunks), 3)
        self.assertChunksCountUpTo30()

