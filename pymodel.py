from enum import Enum

from model import Table, Column


class PyType(Enum):
    INT = (0, "int")
    FLOAT = (1, "float")
    TIME = (2, "int")
    STR = (3, "str")


class PdmToPyColumnType(Enum):
    """
    数据类型
    """
    BYTE = (0, PyType.INT)
    TINYINT = (1, PyType.INT)
    SMALLINT = (2, PyType.INT)
    MEDIUMINT = (3, PyType.INT)
    INT = (4, PyType.INT)
    INTEGER = (4, PyType.INT)
    BIGINT = (5, PyType.INT)
    FLOAT = (6, PyType.FLOAT)
    DOUBLE = (7, PyType.FLOAT)
    DECIMAL = (8, PyType.FLOAT)
    NUMERIC = (8, PyType.FLOAT)
    NUMBER = (9, PyType.INT)
    DATE = (10, PyType.TIME)
    TIME = (11, PyType.TIME)
    YEAR = (12, PyType.TIME)
    DATETIME = (13, PyType.TIME)
    TIMESTAMP = (14, PyType.TIME)
    CHAR = (15, PyType.STR)
    VARCHAR = (16, PyType.STR)
    TINYBLOB = (17, PyType.STR)
    TINYTEXT = (18, PyType.STR)
    BLOB = (19, PyType.STR)
    TEXT = (20, PyType.STR)
    MEDIUMBLOB = (21, PyType.STR)
    MEDIUMTEXT = (22, PyType.STR)
    LONGBLOB = (23, PyType.STR)
    LONGTEXT = (24, PyType.STR)


BASE_MODEL_CLASS = "BaseModel"
FILE_PREFIX = """import time


def format_timestamp(t: int):
    if t is None:
        return None
    localTime = time.localtime(t)
    return time.strftime("%Y-%m-%d %H:%M:%S", localTime)


class BaseModel:
    table_name = None
    id_sequence = 0

    def __init__(self):
        self.__class__.id_sequence += 1
        self.id = self.__class__.id_sequence

    def get_insert_sql(self):
        attrs = self.__dict__
        keys = str(tuple(attrs.keys())).replace("'", "")
        vals = str(tuple(attrs.values())).replace("None", "NULL")
        return "INSERT INTO %s %s VALUE %s;" % (self.__class__.table_name, keys, vals)


"""


def generate_pymodel(tables: list, table_prefix: str = None, ignore_columns: list = None) -> str:
    content = FILE_PREFIX
    for table in tables:
        try:
            content += __generate_pymodel(table, table_prefix, BASE_MODEL_CLASS, ignore_columns) + "\n\n"
        except Exception as e:
            # print("-- %s表创建语句生成失败: %s\n\n" % (table.code, str(e)))
            pass
    return content


def __generate_pymodel(table: Table, table_prefix: str = None, base_class: str = None,
                       ignore_columns: list = None) -> str:
    if ignore_columns is None:
        ignore_columns = []
    else:
        ignore_columns = [c.lower() for c in ignore_columns]
    clz_name = __build_py_class_name(table.code, table_prefix)
    content = "# %s\n" % table.name
    content += "class %s%s:\n" % (clz_name, "" if base_class is None else "(" + base_class + ")")
    content += '\ttable_name = "%s"\n\n' % table.code.lower()
    content += "\tdef __init__(self, "
    for col in table.columns:
        if col.code.lower() not in ignore_columns:
            content += __build_init_arg_code(col) + ", "
    content = content[:-2] + "):\n"
    if base_class is not None:
        content += "\t\t%s.__init__(self)\n" % base_class
    for col in table.columns:
        if col.code.lower() not in ignore_columns:
            content += "\t\t" + __build_init_assign_code(col) + "\n"
    return content


def __build_py_class_name(table_name: str, table_prefix: str = None) -> str:
    """
    将下划线分割命名转为驼峰法类名
    :param table_name: 数据库表名（下划线分割命名）
    :param table_prefix: 表前缀（不加入到类名中）
    :return: 转化后的类名
    """
    table_name = table_name.lower()
    if table_prefix is not None and table_name.startswith(table_prefix):
        table_name = table_name[len(table_prefix):]
    try:
        idx = 0
        while True:
            idx = table_name.index("_", idx)
            table_name = table_name[:idx] + table_name[idx + 1:idx + 2].upper() + table_name[idx + 2:]
    except ValueError as e:
        pass
    return table_name[0].upper() + table_name[1:]


def __build_init_arg_code(column: Column) -> str:
    pyType = PdmToPyColumnType[column.col_type._name_].value[1]
    return column.code.lower() + ": " + pyType.value[1] + " = None"


def __build_init_assign_code(column: Column) -> str:
    content = "self.%s = " % column.code.lower()
    pyType = PdmToPyColumnType[column.col_type._name_].value[1]
    if pyType == PyType.TIME:
        content += "format_timestamp(%s)" % column.code.lower()
    else:
        content += column.code.lower()
    return content

# from pdm_parser import parse_pdm
#
# tables = parse_pdm("/Users/liyilin/Workspace/doc/company/AIFactory-train-doc/06 数据模型/deepminer-v2(1).pdm")
# print(generate_pymodel(tables, table_prefix="deeplearn_", ignore_columns=["id"]))
