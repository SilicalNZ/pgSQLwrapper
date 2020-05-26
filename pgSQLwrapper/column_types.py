from functools import wraps
from datetime import datetime


def auto_joiner(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        string = func(*args, **kwargs)
        string = filter(lambda x: x != None, string)
        return ' '.join(string)

    return wrapper


class OnGet:
    def __init__(self):
        self._column_owner = None

    def __get__(self, instance, owner):
        self._column_owner = owner if self._column_owner is None else self._column_owner
        return self


class CreateTable(OnGet):
    @auto_joiner
    def table_create(self):
        if self._column_owner is not None:
            return self.table_create_referenced()

        string = [self.__class__._column_name(),
            "PRIMARY KEY" if self.PRIMARY_KEY else None,
            "UNIQUE" if self.UNIQUE else None,
            f"DEFAULT {self.DEFAULT}" if self.DEFAULT is not None else None
            ]
        return string

    def table_create_referenced(self):
        column_name = self._column_name() if not hasattr(self, '_on_reference') else self._on_reference._column_name()
        string = [column_name,
            f"REFERENCES {self._column_owner._table_name}"
            ]
        return string


class Column(CreateTable):
    def __init__(self, UNIQUE=False, PRIMARY_KEY=False, DEFAULT=None, REFERENCES=None):
        self.UNIQUE = UNIQUE
        self.PRIMARY_KEY = PRIMARY_KEY
        self.DEFAULT = DEFAULT
        self.REFERENCES = REFERENCES
        super().__init__()

    @classmethod
    def _column_name(cls):
        return cls.__name__.lower()


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
    _on_reference = Integer
    pass


class Boolean(Column):
    pass
