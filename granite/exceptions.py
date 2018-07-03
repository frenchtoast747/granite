"""
Exceptions.
"""


class GraniteException(Exception):
    """Base Exception class for all exceptions."""


class MisconfiguredError(GraniteException):
    """A class or Mixin is misconfigured."""
