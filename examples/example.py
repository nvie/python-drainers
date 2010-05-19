import sys
import threading
import drainers

vars = {}

def abort():
    vars['abort'] = True

def should_abort():
    abort = vars['abort']
    sys.stdout.write('\npoll!\n')
    sys.stdout.flush()
    return abort

def handle_line(line, is_err):
    if is_err:
        vars['err'] += 1
    else:
        vars['out'] += 1
    show_totals()

def show_totals():
    sys.stdout.write("\rout = %d, err = %d" % (vars['out'], vars['err']))
    sys.stdout.flush()

vars['err'] = 0
vars['out'] = 0

test_cmds = [
    ['find', '/'],        # Takes long!
    ['cat', '/dev/null'], # Super fast
    ['ls', '-la'],        # Regular fast
    ['yes'],              # Runs endlessly
]

t = None

for cmd in test_cmds:
    vars['abort'] = False
    vars['err'] = 0
    vars['out'] = 0

    # Set off timer
    t = threading.Timer(5.0, abort)
    t.start()

    print
    print '==> Running %s' % ' '.join(cmd)
    #p = Popen(cmd, bufsize=0, shell=False, stdout=PIPE, stderr=PIPE)
    d = drainers.Drainer(# Popen args first
                         cmd, bufsize=0, shell=False,

                         # Then, the drainer args
                         should_abort_cb=should_abort,
                         read_event_cb=handle_line,
                         check_interval=1.0)
    retcode = d.start()
    print
    print 'Exit code: %d' % retcode

    print
    print 'Total line count:'
    show_totals()
    print

print
print 'Done.'
