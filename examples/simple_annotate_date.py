"""
Annotate each line coming in with the current date.

Example runs:
python simple_annotate_date.py find .
python simple_annotate_date.py cat      (and start typing in stdin)
python simple_annotate_date.py grep 'foobar' *
"""
import sys
import datetime
import drainers

def annotate(line, is_err):
    if is_err:
        stream = sys.stderr
    else:
        stream = sys.stdout
    stream.write('[%s] ' % datetime.datetime.now())
    stream.write('ERROR: ')
    stream.write(line)

d = drainers.Drainer(sys.argv[1:], read_event_cb=annotate)
d.start()
