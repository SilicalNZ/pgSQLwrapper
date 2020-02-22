# pgSQLwrapper
A metaclass that removes boilerplate code when writing pgSQL queries

# Installation
```
python3 -m pip install -U git+https://github.com/SilicalNZ/pgSQLwrapper
```

# Requirements
```
- Python 3.6
- asyncio
- asyncpg
```


# Example
```
import asyncpg
import asyncio
from pgSQLwrapper import pgSQLwrapper

loop = asyncio.get_event_loop()
conn = loop.run_until_complete(asyncpg.create_pool())


# Without package
class Database():
    def __init__(self, conn):
        self.conn = conn

    async def fetch_stats(self, limit): 
        query = """SELECT *
                FROM table
                LIMIT $1
        """
        return await self.conn.exeute(query, limit)

# With package
class Database(metaclass=pgSQLwrapper()):
    def __init__(self, conn):
        self.conn = conn

    # prefix meth with fetch or execute
    def fetch_stats(self, limit):  # branding `async def` is optional
        """SELECT *
        FROM table
        LIMIT $1
        """

db = Database(conn)
print(loop.run_until_complete(db.fetch_stats(limit=2)))
```