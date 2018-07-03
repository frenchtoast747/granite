"""
Utilities for tests.
"""
import os
import shutil


def safe_remove(path):
    if os.path.isdir(path):
        return shutil.rmtree(path, ignore_errors=True)
    try:
        os.remove(path)
    except OSError:
        pass
