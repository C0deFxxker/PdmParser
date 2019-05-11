import xml.sax
from model import Table, Column, PdmColumnType


class PdmXmlHandler(xml.sax.ContentHandler):
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
        self.tables = []
        self.table_map = {}
        self.refs = {}
        self.current_table = None
        self.current_column = None
        self.current_attr = None
        self.current_ref = None
        self.current_parent_table = None
        self.current_child_table = None

    def startDocument(self):
        self.tables = []
        self.table_map = {}
        self.refs = {}
        self.current_table = None
        self.current_column = None
        self.current_attr = None
        self.current_ref = None
        self.current_parent_table = None
        self.current_child_table = None

    # 元素开始事件处理
    def startElement(self, tag, attributes):
        if tag == "o:Table" and "Id" in attributes:
            self.current_table = {'id': attributes["Id"], 'columns': []}
        elif tag == "o:Column":
            self.current_column = {}
        elif tag == "a:Name":
            self.current_attr = "name"
        elif tag == "a:Code":
            self.current_attr = "code"
        elif tag == "a:DataType":
            self.current_attr = "col_type"
        elif tag == "a:Length":
            self.current_attr = "length"
        elif tag == "a:Comment":
            self.current_attr = "comment"
        elif tag == "o:Reference":
            self.current_ref = {}
        elif self.current_ref is not None and tag == "c:ParentTable":
            self.current_parent_table = {}
        elif self.current_ref is not None and tag == "c:ChildTable":
            self.current_child_table = {}
        elif tag == "o:Table" and "Ref" in attributes:
            if self.current_parent_table is not None:
                self.current_parent_table = attributes['Ref']
            elif self.current_child_table is not None:
                self.current_child_table = attributes['Ref']

    # 元素结束事件处理
    def endElement(self, tag):
        if tag == "o:Table" and self.current_table is not None:
            if "code" in self.current_table.keys():
                t = Table()
                for key, val in self.current_table.items():
                    t.__setattr__(key, val)
                self.tables.append(t)
            self.current_table = None
            self.table_map[t.id] = t
        elif tag == "o:Column":
            if "name" in self.current_column.keys():
                c = Column()
                for key, val in self.current_column.items():
                    if key == 'col_type':
                        c.col_type = PdmColumnType[val.upper()]
                    else:
                        c.__setattr__(key, val)
                self.current_table['columns'].append(c)
            self.current_column = None
        elif tag == "a:Name":
            self.current_attr = None
        elif tag == "a:Code":
            self.current_attr = None
        elif tag == "a:DataType":
            self.current_attr = None
        elif tag == "a:Comment":
            self.current_attr = None
        elif tag == "o:Reference" and 'child' in self.current_ref.keys() and 'parent' in self.current_ref.keys():
            if self.current_ref['child'] not in self.refs.keys():
                self.refs[self.current_ref['child']] = []
            ref = self.refs[self.current_ref['child']]
            ref.append(self.current_ref['parent'])
            self.current_ref = None
        elif self.current_ref is not None and tag == "c:ParentTable":
            self.current_ref['parent'] = self.current_parent_table
            self.current_parent_table = None
        elif self.current_ref is not None and tag == "c:ChildTable":
            self.current_ref['child'] = self.current_child_table
            self.current_child_table = None

    # 内容事件处理
    def characters(self, content):
        if self.current_column is not None and self.current_attr is not None:
            self.current_column[self.current_attr] = content
        elif self.current_table is not None and self.current_attr is not None:
            self.current_table[self.current_attr] = content

    def endDocument(self):
        for id in self.refs.keys():
            tb = self.table_map[id]
            childrenId = self.refs[id]
            for childId in childrenId:
                child = self.table_map[childId]
                tb.refs.append(child)


def parse_pdm(pdm_path: str) -> list:
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    handler = PdmXmlHandler()
    parser.setContentHandler(handler)
    parser.parse(pdm_path)
    return handler.tables

# tables = parse_pdm("/Users/liyilin/Workspace/doc/company/AIFactory-train-doc/06 数据模型/deepminer-v2(1).pdm")
#
# max_len = [0, 0]
# for table in tables:
#     for c in table.columns:
#         max_len[0] = max(len(str(c.code)), max_len[0])
#         max_len[1] = max(len(str(c.col_type)), max_len[1])
#
# for table in tables:
#     print("Table:")
#     print("\tName\t: %s" % table.name)
#     print("\tCode\t: %s" % table.code)
#     print("\tComment\t: %s" % (table.comment if table.comment is not None else ""))
#     print("\tColumns\t:")
#     for c in table.columns:
#         print("\t\t%-25s\t\t%-10s\t\t%s\t%s" % (
#         c.code, c.col_type, c.name, "" if c.comment is None else c.comment.strip()))
#     print()
