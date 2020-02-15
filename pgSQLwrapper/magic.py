import inspect
from functools import wraps


def func_generator(name, request, query, func):
    @wraps(func)
    async def wrapper(self, *args):
        return await request(query, *args)
    return wrapper


def startswith_any(string, starters):
    for i in starters:
        if string.startswith(i):
            return i


def pgSQLwrapper(conn):
    class _SQLHandler(type):
        binders = {
            'fetch': conn.fetch,
            'execute': conn.execute}

        def __new__(cls, name, bases, attrs):
            if name.startswith('None'):
                return

            for attrname, attrvalue in attrs.items():
                if attrname.startswith('_'):
                    continue

                query = attrvalue.__doc__
                caller = cls.binders[startswith_any(attrname, cls.binders.keys())]

                attrs[attrname] = func_generator(attrname, caller, query, attrvalue)

            return super().__new__(cls, name, bases, attrs)

        def __init__(self, name, bases, attrs):
            super().__init__(name, bases, attrs)

    return _SQLHandler
