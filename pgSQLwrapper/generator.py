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
    def __init__(self, UNIQUE=False, PRIMARY_KEY=False, DEFAULT=None, REFERENCES=None):
        self.UNIQUE = UNIQUE
        self.PRIMARY_KEY = PRIMARY_KEY
        self.DEFAULT = False

    def _parsed_string(self):
        string = [self.__class__.__name__.lower(),
         "PRIMARY KEY" if self.PRIMARY_KEY else None,
         "UNIQUE" if self.UNIQUE else None,
         f"DEFAULT {self.DEFAULT}" if self.DEFAULT != None else None]
        string = filter(lambda x: x != None, string)
        return ' '.join(string)



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


class Boolean(Column):
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
        id = Integer()
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


    print(ScoreVariation.id._parsed_string())



"""
Parent lookup to find references


"""