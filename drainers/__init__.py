"""
drainers -- Event-based process monitoring.
"""

VERSION = (0, 0, 1)

__version__ = ".".join(map(str, VERSION[0:3])) + "".join(VERSION[3:])
__author__ = "Vincent Driessen"
__contact__ = "vincent@datafox.nl"
__homepage__ = "http://github.com/nvie/python-drainers/"
#__docformat__ = "restructuredtext"

from drainer import Drainer
from drainer import STDIN, STDOUT, STDERR

__all__ = [ 'Drainer', 'STDIN', 'STDOUT', 'STDERR' ]
