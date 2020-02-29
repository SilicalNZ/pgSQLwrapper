import inspect
from functools import wraps


def decorator(db_request=None):
    def funky(func):
        nonlocal db_request
        if db_request is None:
            db_request = func.__name__.split('_')[0]

        query = func.__doc__

        asyncpg_meth = None
        @wraps(func)
        async def wrapper(self_or_conn, *args):
            nonlocal asyncpg_meth
            if asyncpg_meth is None:
                try:
                    conn = getattr(self_or_conn, 'conn')
                except AttributeError:
                    conn = self_or_conn
                asyncpg_meth = getattr(conn, db_request)
            return await asyncpg_meth(query, *args)
        return wrapper
    return funky


def startswith_any(string, starters):
    for i in starters:
        if string.startswith(i):
            return i


def pgSQLwrapper(binders=None):
    """
    :param binders: Customize method prefixes
    """
    if binders is None:
        binders = {
            'fetch': 'fetch',
            'execute': 'execute'}

    class _SQLHandler(type):
        def __new__(cls, name, bases, attrs):
            if name.startswith('None'):
                return

            for attrname, attrvalue in attrs.items():
                if attrname.startswith('_'):
                    continue

                query = attrvalue.__doc__
                request = binders[startswith_any(attrname, binders.keys())]

                attrs[attrname] = decorator(db_request=request)(attrvalue)

            return super().__new__(cls, name, bases, attrs)

        def __init__(self, name, bases, attrs):
            super().__init__(name, bases, attrs)

    return _SQLHandler
