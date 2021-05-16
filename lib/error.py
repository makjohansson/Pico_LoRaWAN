"""
Errors and exceptions defined
"""

class Error(Exception):
    """Base class for other exceptions"""
    pass

class RAK811TimeoutError(Error):
    """Raised when uart response timeout"""
    pass