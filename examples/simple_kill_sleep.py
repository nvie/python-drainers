"""
Simply call "sleep 10", but terminate earlier.
"""
import sys
import threading
import drainers

def ignore(x,y):
    pass

# Keep a time-out flag that is set after 3 seconds
timed_out = False

def poll():
    sys.stdout.write('Checking... ')
    if timed_out:
        sys.stdout.write('Should quit now!\n')
    else:
        sys.stdout.write('OK\n')
    sys.stdout.flush()
    return timed_out

# Set the global flag!
def time_out():
    global timed_out
    timed_out = True

# Start the timer to flip the flag
t = threading.Timer(3.0, time_out)
t.daemon = True
t.start()

d = drainers.Drainer(['sleep', '10'], read_event_cb=ignore,
                                      should_abort_cb=poll,
                                      check_interval=0.5)    # Poll every half second
d.start()
print 'Done.'
