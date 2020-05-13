from datetime import datetime
import time
import random

from pgSQLwrapper.magic import decorator, pgSQLwrapper

def random_id():
    y = [i for i in str(time.time_ns())]
    random.shuffle(y)
    y = int(''.join(y))
    return y


class Column:
    def __init__(self, name, extra_stuff='', primary_key=False, references=''):
        self.name = name
        self.references = references
        self.primary_key = primary_key
        self.extra_stuff = extra_stuff

        if self.primary_key:
            self.extra_stuff += 'PRIMARY KEY'

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


class Generate:
    @classmethod
    def create_table(cls, table_name, columns):
        def execute_create_table(self):
            pass

        query = (
            f'WITH {random_id()} as (\n'
            f'    CREATE TABLE IF NOT EXISTS {table_name}(\n'
            f'    {", ".join([i.parsed_string() for i in columns])}))'
        )

        execute_create_table.__doc__ = query
        return execute_create_table

    @classmethod
    def insert(cls, table_name, columns):
        def execute_insert(self, *args):
            pass

        query = (
            f'WITH {random_id()} as (\n'
            f'    INSERT INTO {table_name}(\n' 
            f'    {", ".join([i.name for i in columns if not i.primary_key])})\n'
            f'    VALUES(${", $".join(map(str, range(1, len(columns))))}))'
        )
        execute_insert.__doc__ = query
        return execute_insert

    @classmethod
    def merge(merge, query, other_query):
        query = (
            f'{query.__doc__},\n'
            f'{other_query.__doc__.replace("WITH ", "")}'
        )
        other_query.__doc__ = query




class _pgSQLgenerator(pgSQLwrapper):
    def __new__(cls, name, bases, attrs):
        if name.startswith('None'):
            return
        if name.startswith('Table'):
            return super().__new__(cls, name, bases, attrs)

        attrs['execute_create_table'] = Generate.create_table(attrs['name'], attrs['columns'])
        attrs['execute_insert'] = Generate.insert(attrs['name'], attrs['columns'])

        if len(bases) > 1:
            ocls = bases[-1]
            Generate.merge(getattr(ocls, 'execute_create_table'), attrs['execute_create_table'])
            Generate.merge(getattr(ocls, 'execute_insert'), attrs['execute_insert'])


        return super().__new__(cls, name, bases, attrs)

    @classmethod
    async def create_pool(cls, **credentials):
        conn = await asyncpg.create_pool(**credentials)
        return cls(conn)


class Table(metaclass=_pgSQLgenerator):
    def execute_create_table(self):
        raise NotImplemented()

    def execute_insert(self):
        raise NotImplemented()



if __name__ == '__main__':
    class Score(Table):
        columns = [
            Integer('id', primary_key=True),
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


    class ScoreStat(Score):
        columns = [
            Integer('id', references='score'),
            Integer('average_damage'),
            Integer('time_elapsed'),
            Integer('highest_damage'),
            SmallInt('wave_reached'),
            Integer('distance_reached'),
            Integer('total_damage'),
            Integer('damage_taken'),
            SmallInt('level_reached')
        ]

        name = 'score_stats'

    t = ScoreStat()

    print(t.execute_insert.__doc__)