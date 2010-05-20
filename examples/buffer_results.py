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

def crunch(files):
    print 'Setting up cruncher...'
    setup_cruncher()
    while len(files) > 0:
        f = files.pop(0)
        print '- Crunching file %s...' % f.strip()
        do_something_expensive(f)
    print 'Releasing cruncher...'
    destroy_cruncher()

def add_to_buffer(line, is_err):
    if is_err:
        # ignore all errors
        return
    files.append(line)

    # start crunch synchronously after 20 items have been read
    if len(files) >= 20:
        crunch(files)

d = drainers.Drainer(['find', '.', '-type', 'f'], read_event_cb=add_to_buffer)
d.start()
