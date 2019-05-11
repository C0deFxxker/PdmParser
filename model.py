from enum import Enum


class PdmColumnType(Enum):
    """
    数据类型
    """
    BYTE = 0
    TINYINT = 1
    SMALLINT = 2
    MEDIUMINT = 3
    INT = 4
    INTEGER = 4
    BIGINT = 5
    FLOAT = 6
    DOUBLE = 7
    DECIMAL = 8
    NUMERIC = 8
    NUMBER = 9
    DATE = 10
    TIME = 11
    YEAR = 12
    DATETIME = 13
    TIMESTAMP = 14
    CHAR = 15
    VARCHAR = 16
    TINYBLOB = 17
    TINYTEXT = 18
    BLOB = 19
    TEXT = 20
    MEDIUMBLOB = 21
    MEDIUMTEXT = 22
    LONGBLOB = 23
    LONGTEXT = 24

    def __str__(self):
        return self._name_


class Table:
    def __init__(self, id: int = None, name: str = None, code: str = None, comment: str = None, refs=None):
        if refs is None:
            refs = []
        self.id = id
        self.name = name
        self.code = code
        self.comment = comment
        self.columns = []
        # 关联主表
        self.refs = refs

    def __str__(self):
        return str(self.__dict__)


class Column:
    def __init__(self, name: str = None, code: str = None, col_type: PdmColumnType = None, col_length: int = None,
                 pk: bool = False, not_null: bool = False, comment: str = None):
        self.name = name
        self.code = code
        self.col_type = col_type
        self.col_length = col_length
        self.pk = pk
        self.not_null = not_null
        self.comment = comment

    def __str__(self):
        return str(self.__dict__)
