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

class Database(metaclass=pgSQLwrapper(conn)):
    def fetch(self):  # branding `async def` is optional
        """SELECT *
        FROM table
        LIMIT 1
        """

db = Database()

print(loop.run_until_complete(db.fetch()))
```