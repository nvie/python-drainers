===================================================
 drainers - Event-based draining of process output
===================================================

drainers is an abstraction around `subprocess.Popen` to read and control
process output event-wise.  It also allows you to abort running processes
either gracefully or forcefully without having to directly interact with the
processes or threads themself.

Overview
========

Defining a process
------------------
A `Drainer` is a factory and controller wrapper around
`subprocess.Popen` and therefore takes all of the (optional) parameters
that `subprocess.Popen`'s initializer takes.  For example, the minimal
`Drainer` takes a command array::

	from drainers import Drainer

	def ignore_event(line, is_err):
		pass

	my_drainer = Drainer(['ls', '-la'], read_event_cb=ignore_event)
	my_drainer.start()

But, extra arguments are allowed, too::

	my_drainer = Drainer(['echo', '$JAVA_HOME'], shell=True, bufsize=64,
						 read_event_cb=ignore_event)
	my_drainer.start()

The only two arguments to `Drainer` that are reserved are
`stdout` and `stderr`.  `Drainer` requires them to be
`subprocess.PIPE` explicitly, and sets them for you accordingly.

Defining a callback
-------------------
`Drainer`'s strength lies in the fact that each line that is read from the
process' standard output or standard error streams leads to a callback
function being invoked.  This allows you to process virtually any process'
output, as long as it's line-based.

The callback function can be specified using the `read_event_cb` parameter to
the constructor, as seen in the example above.  It is mandatory.  The callback
function specified needs to have a specific signature::

	def my_callback(line, is_err):
		...

It should take two parameters: `line` (a string) and `is_err` (a boolean).
The latter indicates that the line is read from the standard error stream.
There is nothing more to it.  It does not need to return anything: it's return
value will be ignored.  Your callback may be a class method, too, like in the
following example.  Notice that in those cases, you pass `foo.my_method` as
the value for the `read_event_cb` parameter::

	class MyClass(object):

		def my_method(self, line, is_err):
			...
	
	foo = MyClass()
	my_drainer = Drainer(['ls'], read_event_cb=foo.my_method)
	my_drainer.start()

The granularity currently is a single line.  If you want to read predefined
chunks (lines) of data, use `BufferedDrainer` instead.  See
examples/buffer_results.py for an example.

Aborting processes
------------------
`Drainer` allows you to abort a running process in the middle of execution,
forcefully sending the process a `terminate()` message (Python equivalent of a
Unix `SIGTERM` message) when a certain condition arises.  By default, the
process will never be terminated abnormally.  To specify termination criteria,
implement a callback function that takes no parameters and returns `True` if
abortion is desired and `False` otherwise.  For example, for a long running
process you might want to terminate it if the disk is getting (almost) full.
But checking how much space is free can be a lengthy operation, so you might
want to do it only sparingly::

	def out_of_diskspace():
		left = handytools.check_disk_free()
		total = handytools.check_disk_total()
		return (left / total) < 0.03

	# The following drainer executes the cruncher and checks whether the disk
	# is (almost) full every 5 seconds.  It aborts if free disk space runs
	# under 3%.
	my_drainer = Drainer(['/bin/crunch', 'inputfile', 'outputfile'],
	                     read_event_cb=ignore_event,
						 should_abort=out_of_diskspace,
						 check_interval=5.0)
	exitcode = my_drainer.start()

The example is pretty self-explaining.  You can check the exitcode to see the
result of the process.


More examples
=============
See the `examples` directory for more detailed examples.
