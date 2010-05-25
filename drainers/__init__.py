"""
drainers -- Event-based process monitoring.
"""

VERSION = (0, 0, 2)

__version__ = ".".join(map(str, VERSION[0:3])) + "".join(VERSION[3:])
__author__ = "Vincent Driessen"
__contact__ = "vincent@datafox.nl"
__homepage__ = "http://github.com/nvie/python-drainers/"
#__docformat__ = "restructuredtext"

from base import Drainer
from buffered import BufferedDrainer

__all__ = [ 'Drainer', 'BufferedDrainer' ]
