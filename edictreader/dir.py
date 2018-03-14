import os
import inspect

MODULE_ROOT = os.path.abspath(os.path.dirname(inspect.getframeinfo(inspect.currentframe()).filename))


def database_path(database):
    return os.path.join(MODULE_ROOT, 'database', database)
