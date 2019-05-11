from enum import Enum

from model import Table, PdmColumnType


class DbType(Enum):
    MYSQL = 0
    ORACLE = 1
    SQLSERVER = 2
    H2 = 3


class PdmToMySqlColumnType(Enum):
    """
    PDM与MySQL字段类型映射
    """
    BYTE = ("BYTE", None)
    TINYINT = ("TINYINT", None)
    SMALLINT = ("SMALLINT", None)
    MEDIUMINT = ("MEDIUMINT", None)
    INT = ("INT", None)
    INTEGER = ("INTEGER", None)
    BIGINT = ("BIGINT", None)
    FLOAT = ("FLOAT", None)
    DOUBLE = ("DOUBLE", None)
    DECIMAL = ("DECIMAL", (9, 2))
    NUMERIC = ("NUMERIC", (9, 2))
    NUMBER = ("BIGINT", None)
    DATE = ("DATE", None)
    TIME = ("TIME", None)
    YEAR = ("YEAR", None)
    DATETIME = ("DATETIME", None)
    TIMESTAMP = ("TIMESTAMP", None)
    CHAR = ("CHAR", 50)
    VARCHAR = ("VARCHAR", 255)
    TINYBLOB = ("TINYBLOB", 255)
    TINYTEXT = ("TINYTEXT", 255)
    BLOB = ("BLOB", 255)
    TEXT = ("TEXT", 255)
    MEDIUMBLOB = ("MEDIUMBLOB", 65535)
    MEDIUMTEXT = ("MEDIUMTEXT", 65535)
    LONGBLOB = ("LONGBLOB", 65535)
    LONGTEXT = ("LONGTEXT", 65535)

    def __str__(self):
        return self._name_


def generate_sql(tables: list, db_type: DbType) -> str:
    if db_type == DbType.MYSQL:
        content = ""
        for table in tables:
            content += generate_sql(table, db_type) + "\n\n"
        return content
    raise Exception("不支持数据库类型")


def generate_sql(table: Table, db_type: DbType) -> str:
    content = ""
    if len(table.columns) == 0:
        raise Exception("%s表没有字段" % table.code)
    if db_type == DbType.MYSQL:
        content += "-- ----------------------------\n"
        content += "-- Table structure for %s\n" % table.code.lower()
        content += "-- ----------------------------\n"
        content += "DROP TABLE IF EXISTS `%s`;\n" % table.code.lower()
        content += "CREATE TABLE `%s`(\n" % table.code.lower()
        for col in table.columns:
            col_type = get_db_col_type(db_type, col.col_type, col.col_length)
            not_null = "NULL" if col.not_null is None or not col.not_null else "NOT NULL"
            pk = "" if col.pk is None or not col.pk else " PRIMARY KEY"
            comments = " COMMENT '%s%s'" % (
                col.name, "" if col.comment is None or len(col.comment.strip()) == 0 else "\t" + col.comment.strip())
            content += "  `%s` %s %s%s%s,\n" % (col.code, col_type, not_null, pk, comments)
        if content[-2] == ',':
            content = content[:-2] + "\n"
        content += ")%s;\n" % ("" if table.comment is None else " COMMENT = '" + table.comment.strip() + "'")
        return content
    raise Exception("不支持数据库类型")


def get_db_col_type(db_type: DbType, pdm_type: PdmColumnType, col_length: int = None) -> str:
    if db_type == DbType.MYSQL:
        mysqlColType, defaultLen = PdmToMySqlColumnType[pdm_type._name_].value
        if col_length is not None:
            mysqlColLen = "(%d)" % col_length
        elif defaultLen is not None:
            mysqlColLen = "(%s)" % str(defaultLen)
            mysqlColLen = mysqlColLen.replace("((", "(").replace("))", ")")
        else:
            mysqlColLen = ""
        return mysqlColType + mysqlColLen
    raise Exception("不支持数据库类型")

# from pdm_parser import parse_pdm
#
# tables = parse_pdm("/Users/liyilin/Workspace/doc/company/AIFactory-train-doc/06 数据模型/deepminer-v2(1).pdm")
# for table in tables:
#     try:
#         print(generate_sql(table, DbType.MYSQL))
#     except Exception as e:
#         print("-- %s表创建语句生成失败: %s\n\n" % (table.code, str(e)))
