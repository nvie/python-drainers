"""
Simple finder. Search for the file given in sys.argv[1] for a maximum of
10 seconds, then abort.  Present results of found files and errors.

For the best demonstration effect, make the find run long (for example,
run the script from /).

Example runs:
python simple_find.py <somefile>
"""
import sys
import drainers
import threading

class Finder(object):
    def __init__(self):
        self.errors = []
        self.found = []
        self.timed_out = False

    def time_out(self):         # will be invoked by threading.Timer() after 10 secs
        self.timed_out = True

    def has_timed_out(self):
        return self.timed_out

    def handle_line(self, line, is_err):
        if is_err:
            self.errors.append(line)
        else:
            self.found.append(line)

    def main(self, search_for):
        d = drainers.Drainer(['find', '.', '-name', search_for],
                             read_event_cb=self.handle_line,
                             should_abort_cb=self.has_timed_out)

        t = threading.Timer(10.0, self.time_out)
        t.daemon = True
        t.start()

        print 'Finding files called "%s" for 10 seconds...' % search_for
        exitcode = d.start()

        print 'Return code was: %d' % exitcode
        print ''
        print 'Found:'
        print ''.join(self.found)
        print ''
        print 'Errors:'
        print ''.join(self.errors)

finder = Finder()
finder.main(sys.argv[1])
