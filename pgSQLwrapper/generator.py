import time
import random

from pgSQLwrapper.sql_from_docstring import decorator, pgSQLwrapper
from pgSQLwrapper.column_types import *

def random_id():
    y = [i for i in str(time.time_ns())]
    random.shuffle(y)
    y = int(''.join(y))
    return y


class Generate:
    def __init__(self, table_name, columns):
        self.table_name = table_name
        self.columns = columns

    def _wrapper_with(self):
        return f'WITH {func()}'

    def _wrapper_as(self, func):
        return f'{self.table_name} as ({func()})'

    def _core_columns(self, joiner):
        return joiner.join([f"{key} {value.parsed_string()}" for key, value in self.columns.items()])

    def _core_create_table(self):
        columns = self._core_columns(",\n    ")
        return (
            f'CREATE TABLE IF NOT EXISTS {self.table_name}('
            f'\n    {columns})'
        )

    def gen_create_table(self):
        def execute_create_table(self):
            pass
        execute_create_table.__doc__ = self._core_create_table()
        return execute_create_table

    @classmethod
    def insert(cls, table_name, columns):
        def execute_insert(self, *args):
            pass

        identifiers = [i.name for i in columns if i.primary_key]
        non_identifiers = [i.name for i in columns if not i.primary_key]
        query = (
            f'WITH {random_id()} as (\n'
            f'    INSERT INTO {table_name}(\n' 
            f'    {", ".join(non_identifiers)})\n'
            f'    VALUES(${", $".join(map(str, range(1, len(non_identifiers) + 1)))}))'
        )
        if identifiers:
            query = query[:-1] + f'\n    RETURNING {", ".join(identifiers)})'
        execute_insert.__doc__ = query
        return execute_insert

    @classmethod
    def delete(cls, table_name, columns):
        pass

    @classmethod
    def merge(merge, query, other_query, table):
        query = (
            f'{query.__doc__},\n'
            f'{other_query.__doc__.replace("WITH ", "")}'
        )
        other_query.__doc__ = query


class _pgSQLgenerator(pgSQLwrapper):
    def __new__(cls, name, bases, attrs, **kwargs):
        attrs['_table_name'] = name.lower() if 'table_name' not in kwargs else kwargs['table_name']

        columns = {key: value for key, value in attrs.items() if issubclass(value.__class__, Column)}

        generator = Generate(attrs['_table_name'], columns)
        attrs['execute_create_table'] = generator.gen_create_table()

        return super().__new__(cls, name, bases, attrs)

    @classmethod
    async def create_pool(cls, **credentials):
        conn = await asyncpg.create_pool(**credentials)
        return cls(conn)


class Table(metaclass=_pgSQLgenerator):
    def __init__(self, conn):
        self.__conn = conn
        self.conn = self.__conn

    def execute_create_table(self):
        raise NotImplemented()

    def execute_insert(self):
        raise NotImplemented()

    def exectute_delete(self):
        raise NotImplemented()




if __name__ == '__main__':
    class User(Table):
        id = Serial(PRIMARY_KEY=True)
        name = Text()
        platform_id = Text()
        platform = Text()
        blocked = Boolean(DEFAULT=False)


    class Variation(Table):
        id = Serial(PRIMARY_KEY=True)
        name = Text(UNIQUE=True)
        theme = Integer
        blocked = Boolean(DEFAULT=False)


    class Score(Table):
        id = Serial()
        author = Integer()
        build_name = Text()
        shield = Variation.id
        ship = Variation.id
        weapon = Variation.id
        score = Integer()
        time = Integer()
        seed = Text()


    class ScoreStat(Score):
        id = Score.id
        average_damage = Integer()
        time_elapsed = Integer()
        highest_damage = Integer()
        wave_reached = SmallInt()
        distance_reached = Integer()
        total_damage = Integer()
        damage_taken = Integer()
        level_reached = SmallInt()


    class ScoreVariation(ScoreStat, Variation):
        id = Score.id
        mods = Variation.id
        ordering = Integer()


    print(Score(None).execute_create_table.__doc__)



"""
Parent lookup to find references


"""