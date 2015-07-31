__author__ = 'ArmiT'


class AppException(Exception):
    """
    Exception for catching application processing errors
    """

    def __init__(self, message, code):
        self.message = message
        self.code = code

    def __str__(self):
        return repr(self.message)
