import inspect
from functools import wraps


def func_generator(name, request, query, func):
    @wraps(func)
    async def wrapper(self, *args):
        conn = getattr(self, 'conn')
        asyncpg_meth = getattr(conn, request)
        return await asyncpg_meth(query, *args)
    return wrapper


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

                attrs[attrname] = func_generator(attrname, request, query, attrvalue)

            return super().__new__(cls, name, bases, attrs)

        def __init__(self, name, bases, attrs):
            super().__init__(name, bases, attrs)

    return _SQLHandler
