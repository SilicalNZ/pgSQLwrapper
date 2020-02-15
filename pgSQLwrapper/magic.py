import inspect


def func_generator(name, request, query, parameters):
    if inspect.iscoroutinefunction(request):
        async def wrapper(self, *args):
            return await request(query, *args)
    else:
        def wrapper(self, *args):
            return request(query, *args)
    return wrapper


def pgSQLwrapper(conn):
    class _SQLHandler(type):
        def __new__(cls, name, bases, attrs):
            if name.startswith('None'):
                return
            for attrname, attrvalue in attrs.items():
                if attrname.startswith('_'):
                    continue

                query = attrvalue.__doc__
                parameters = attrvalue.__code__.co_varnames[:attrvalue.__code__.co_argcount]

                if query.startswith('SELECT'):
                    attrs[attrname] = func_generator(attrname, conn.fetch, query, parameters)
                else:
                    attrs[attrname] = func_generator(attrname, conn.execute, query, parameters)

            return super().__new__(cls, name, bases, attrs)

        def __init__(self, name, bases, attrs):
            super().__init__(name, bases, attrs)

    return _SQLHandler
