import time
import threading
import subprocess
import copy

STDIN  = 0
STDOUT = 1
STDERR = 2

class Drainer(object):

    def __init__(self, args, read_event_cb=None, should_abort_cb=None,
                 check_interval=2.0, force_kill_timeout=None, **pargs):
        '''Creates a new Drainer.

           A process monitor initializes the given command (from `cmd`). To
           start draining the pipes and generating the read events, invoke
           `start()`.

           Popen arguments:
           args    -- Args that can be fed to `subprocess.Popen` (see [1]).
           **pargs -- Keyword arguments that can be fed to `subprocess.Popen`
                      (see [1]). Beware that `ProcessMonitor` always sets the
                      `stdout` and `stderr` params to `subprocess.PIPE`.

           Keyword arguments:
           read_event_cb --
                      Callback function that is invoked each time a line of
                      output is read from the subprocess.  This function should
                      take two parameters `line` and `is_err`.  Its return
                      value is ignored. `is_err` is `True` when the line
                      originated from the stderr stream.
           should_abort_cb --
                      Callback function that is invoked periodically (see
                      argument `check_interval`) to check whether the process
                      should terminate. Have the callback function return
                      `True` when the process should be aborted, `False`
                      otherwise.
           check_interval --
                      Time interval in seconds that the `_cbshould_abort_cb`
                      callback function is invoked.  Choose lower for more
                      responsiveness, choose higher for better performance.
                      (Default: 2.0)
           force_kill_timeout --
                      When the streams are read empty, the subprocess will be
                      killed.  `Drainer` will try to `terminate()` the process
                      gracefully, but when the process isn't terminated after
                      `force_kill_timeout`, the process will be force-killed.
                      When not set, the process will never be force-killed.

           Some notes:

           * The `read_event_cb` callback function is surrounded by a thread
             lock. This means that to simultaneous reads (from both stdout and
             stderr) are delivered sequentially. Therefore, it is unnecessary
             to provide your own thread locking in your callback function.

           [1] http://docs.python.org/library/subprocess.html#subprocess.Popen

        '''
        self.check_interval = check_interval
        self.force_kill_timeout = force_kill_timeout
        self.should_abort_cb = should_abort_cb
        self.read_event_cb = read_event_cb

        self._lock = threading.RLock()
        self._cancel_event = threading.Event()
        self._popen_args = copy.copy(args)
        self._popen_kwargs = copy.copy(pargs)

    def _read_stream(self, stream, is_err):
        # Process a line at a time, checking whether the _cancel_event is fired
        while not self._cancel_event.is_set():
            ln = stream.readline()
            if ln != '':
                self._lock.acquire()
                try:
                    self.read_event_cb(ln, is_err)
                finally:
                    self._lock.release()
            else:
                # Terminate normally
                break

    def _read_stdout(self, stream):
        self._read_stream(stream, False)

    def _read_stderr(self, stream):
        self._read_stream(stream, True)

    def _poll_should_abort(self):
        while self.process.poll() is None:   # as long as the process is alive
            if self.should_abort_cb():       # callback should return True if cancelled
                self._cancel_event.set()
                self.process.terminate()
                break
            time.sleep(self.check_interval)

    def _force_kill(self):
        if not self.process.poll() is None:
            self.process.kill()

    def start(self):
        '''Calling this will create the `subprocess.Popen` instance and drain
           the stdout and stderr pipes of the process.  Each time a line is
           read from those pipes, the monitor calls back into the
           `read_event_cb` callback function.

           When a `should_abort_cb` callback function is set, a poller thread
           will be set up to periodically check whether the process should
           terminate.

           Note that `start()` blocks until the process is finished.

           Returns the exitcode of the process.

        '''
        self._popen_kwargs['stdout'] = subprocess.PIPE
        self._popen_kwargs['stderr'] = subprocess.PIPE
        self.process = subprocess.Popen(self._popen_args,
                                        **self._popen_kwargs)

        rerr = threading.Thread(target=self._read_stderr, args=(self.process.stderr,))
        rerr.daemon = True
        rout = threading.Thread(target=self._read_stdout, args=(self.process.stdout,))
        rout.daemon = True

        if not self.should_abort_cb is None:
            poller = threading.Thread(target=self._poll_should_abort)
            poller.daemon = True
            poller.start()

        # Start draining the pipes
        rerr.start()
        rout.start()

        # Wait for stream readers to finish, either normally, or aborted
        rout.join()
        rerr.join()

        # Finally, wait for the poller thread to finish, too (worst
        # case, this can take self.check_interval seconds)
        if not self.should_abort_cb is None:
            poller.join()

        if self.force_kill_timeout is not None:
            kill_timer = threading.Timer(self.force_kill_timeout, self._force_kill)
            kill_timer.start()

        # in case wait() finishes before force_kill_timeout elapsed, we
        # may simply cancel the force_kill timer
        exitcode = self.process.wait()

        if self.force_kill_timeout is not None:
            kill_timer.cancel()

        return exitcode

