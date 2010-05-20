"""
Simply call "ls -a", no special stuff.
"""
import sys
import drainers

counter = 0

def just_echo(line, is_err):
    global counter
    if is_err:
        sys.stdout.write('ERROR: ')
    sys.stdout.write(line)
    counter += 1

d = drainers.Drainer(['ls', '-a'], read_event_cb=just_echo)
d.start()
print '%d lines read' % counter
