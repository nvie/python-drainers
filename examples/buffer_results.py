"""
Process 20 lines of output at a time.

Example runs:
python buffer_results.py
"""
import sys
import time
import drainers

# fake this
def setup_cruncher():
    time.sleep(1)

def do_something_expensive(file):
    time.sleep(0.005)

def destroy_cruncher():
    time.sleep(0.8)

files = []

def crunch(lines):
    print 'Setting up cruncher...'
    setup_cruncher()
    for line, is_err in lines:
        if is_err: # ignore errors
            continue
        print '- Crunching file %s...' % line.strip()
        do_something_expensive(line)
    print 'Releasing cruncher...'
    destroy_cruncher()

d = drainers.BufferedDrainer(['find', '.', '-type', 'f'], read_event_cb=crunch, chunk_size=20)
d.start()
