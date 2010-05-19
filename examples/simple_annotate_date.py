"""
Simply call "ls -a", no special stuff.
"""
import sys
import datetime
import drainers

def annotate(line, is_err):
    sys.stdout.write('[%s] ' % datetime.datetime.now())
    if is_err:
        sys.stdout.write('ERROR: ')
    sys.stdout.write(line)

d = drainers.Drainer(sys.argv[1:], read_event_cb=annotate)
d.start()
