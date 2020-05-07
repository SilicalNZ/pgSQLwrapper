from datetime import datetime
from time import time

from pgSQLwrapper.magic import decorator, pgSQLwrapper


class Column:
    def __init__(self, name, extra_stuff='', references=''):
        self.name = name
        self.references = references
        self.extra_stuff = extra_stuff

    @property
    def invertor(self):
        return self.convertor

    def parsed_string(self):
        string = f'{self.name} {self.__class__.__name__}'
        string += f' {self.extra_stuff}' if self.extra_stuff else ''
        string += ' references ' + self.references if self.references else ''
        return string


class Text(Column):
    convertor = str


class Time(Column):
    convertor = datetime.time


class Integer(Column):
    convertor = int


class SmallInt(Integer):
    pass


class BigInt(Integer):
    pass


class Serial(Column):
    pass



class _pgSQLgenerator(pgSQLwrapper):
    def __new__(cls, name, bases, attrs):
        if name.startswith('None'):
            return

        def execute_create_table(self):
            pass

        name = attrs['name']

        columns = attrs['columns']

        query = f'''CREATE TABLE IF NOT EXISTS {name}
        ({", ".join([i.parsed_string() for i in columns])})'''

        execute_create_table.__doc__ = query
        attrs['execute_create_table'] = execute_create_table

        return super().__new__(cls, name, bases, attrs)

    @classmethod
    async def create_pool(cls, **credentials):
        conn = await asyncpg.create_pool(**credentials)
        return cls(conn)


if __name__ == '__main__':
    class Table(metaclass=_pgSQLgenerator):
        columns = [
            Integer('id', extra_stuff='PRIMARY KEY'),
            Integer('author', references='users'),
            Text('build_name'),
            Integer('shield', references='variation'),
            Integer('ship', references='variation'),
            Integer('weapon', references='variation'),
            Integer('score'),
            Integer('time'),
            Text('seed')
        ]

        name = 'score'


    t = Table()

    print(t.execute_create_table.__doc__)