from base import _BaseDrainer

class BufferedDrainer(_BaseDrainer):

    def __init__(self, args, read_event_cb=None, should_abort_cb=None,
                 check_interval=2.0, force_kill_timeout=None,
                 chunk_size=0,
                 #flush_timeout=None,
                 **pargs):
        '''Creates a new BufferedDrainer.

           For initialization parameters, see the documentation of
           `_BaseDrainer`.

           `BufferedDrainer` adds options to limit the number of times
           the `read_event_cb` callback function is invoked by buffering
           either a fixed number of lines and/or a fixed timeout value.

           Note:
           This implementation expects `read_event_cb` to take a single
           **list** first parameter, instead of a string and a boolean
           parameter.  The list contains `(line, is_err)` tuples for
           each line read.  For example:

               def my_buffered_callback(lines):
                   for line, is_err in lines:
                       # Use familiar `line` and `is_err` variables here
                       ...

           `BufferedDrainer` adds the following arguments to the
           constructor:

           chunk_size -- The size of the buffer (in lines). Chunks of
                         `chunk_size` lines will be passed to
                         `read_event_cb` at once.  This reduces the
                         amount of calls to `read_event_cb`.
                         (Default: disabled, 0)

           #flush_timeout --
           #              A timeout value (in seconds, floating point) to
           #              time-limit buffering.  When `flush_timeout`
           #              elapses, the buffer is flushed by calling
           #              `read_event_cb` with all the lines that are
           #              read so far.
           #              (Default: None)

           If both `chunk_size` and `flush_timeout` are specified, the
           buffer is flushed when either of both conditions is matched.
           When such a flush occurs, the flush timer is reset.

        '''
        super(BufferedDrainer, self).__init__(
            args,
            read_event_cb=self._wrapper,
            should_abort_cb=should_abort_cb,
            check_interval=check_interval,
            force_kill_timeout=force_kill_timeout,
            **pargs)
        self._orig_read_event_cb = read_event_cb
        self.chunk_size = chunk_size
        #self.flush_timeout = flush_timeout
        self._buffer = []

    @property
    def buffer(self):
        return self._buffer

    def _should_flush(self):
        return self.chunk_size <= 0 or \
            len(self.buffer) >= self.chunk_size

    def _wrapper(self, line, is_err):
        tuple = (line, is_err)
        self.buffer.append(tuple)

        if self._should_flush():
            self._flush()

    def _empty_buffer(self):
        '''Empty the buffer and return a copy of it.'''
        bufcopy = []
        while len(self.buffer) > 0:
            bufcopy.append(self.buffer.pop(0))
        return bufcopy

    def _flush(self):
        if len(self.buffer) > 0:
            bufcopy = self._empty_buffer()
            self._orig_read_event_cb(bufcopy)

