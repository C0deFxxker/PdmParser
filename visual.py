import math
import tkinter as tk
import tkinter.font as tkFont

from model import Table, Column

FAKE_CANVAS = tk.Canvas(None)


def get_canvas_text_bound_size(text: str, font):
    """
    计算Canvas中字体的宽高
    :param text: 文本内容
    :param font: 文本字体
    :return: returns a tuple like (width, height)
    """
    t = FAKE_CANVAS.create_text(0, 0, text=text, font=font)
    bound = FAKE_CANVAS.bbox(t)
    return bound[2] - bound[0], bound[3] - bound[1]


class TableRect:
    def __init__(self, root: tk.Canvas, x: int, y: int, table: Table, font: tkFont.Font = "Times 20 italic bold",
                 padding: int = 3, line_width: int = 1):
        self.root = root
        self.x = x
        self.y = y
        self.table = table
        self.font = font
        self.padding = padding
        self.line_width = line_width
        self.width, self.height = self.get_auto_bounding()

    def render(self):
        font_size = self.font.configure()['size']

        # render Box
        self.root.create_rectangle(self.x, self.y, self.x + self.width, self.y + self.height, fill="white")

        # render table name
        x = self.x + self.width / 2
        y = self.y + font_size / 2 + self.padding
        self.root.create_text(x, y, text=self.table.name, font=self.font)

        # render split line
        y = self.y + font_size + self.padding * 2
        self.root.create_line(self.x, y, self.x + self.width, y)

        # render columns name
        sy = y + self.padding
        x = self.x + self.padding
        max_width = 0
        for col in self.table.columns:
            col: Column = col
            self.root.create_text(x, sy, text=col.name, font=self.font, anchor=tk.NW)
            max_width = max(get_canvas_text_bound_size(col.name, self.font)[0], max_width)
            sy += font_size

        # render columns type
        sy = y + self.padding
        x = x + max_width + self.padding
        max_width = 0
        for col in self.table.columns:
            col: Column = col
            text = col.col_type._name_
            if col.col_length is not None:
                text += "(" + str(col.col_length) + ")"
                text = text.replace("((", "(").replace("))", ")")
            self.root.create_text(x, sy, text=text, font=self.font, anchor=tk.NW)
            max_width = max(get_canvas_text_bound_size(text, self.font)[0], max_width)
            sy += font_size
        right = x + max_width + self.padding

    def get_auto_bounding(self):
        left = self.x
        top = self.y
        font_size = self.font.configure()['size']

        # table name + split line
        right = self.x + get_canvas_text_bound_size(self.table.name, self.font)[0] + 2 * self.padding
        y = self.y + font_size + self.padding * 2

        if self.table.columns is None or len(self.table.columns) == 0:
            return right - left, y + self.padding * 2 - top

        # columns name
        sy = y + self.padding
        x = self.x + self.padding
        max_width = 0
        for col in self.table.columns:
            col: Column = col
            max_width = max(get_canvas_text_bound_size(col.name, self.font)[0], max_width)
            sy += font_size

        bottom = sy + self.padding + self.line_width

        # render columns type
        sy = y + self.padding
        x = x + max_width + self.padding
        max_width = 0
        for col in self.table.columns:
            col: Column = col
            text = col.col_type._name_
            if col.col_length is not None:
                text += "(" + str(col.col_length) + ")"
                text = text.replace("((", "(").replace("))", ")")
            max_width = max(get_canvas_text_bound_size(text, self.font)[0], max_width)
            sy += font_size
        right = max(right, x + max_width + self.padding)

        return right - left, bottom - top


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.canvas = None
        self.create_widgets()

        # 滚动用的
        self.cur_pos = None
        self.move = None
        self.sensitivity = 0.05

    def create_widgets(self):
        self.canvas = tk.Canvas(None, width=1024, height=768)
        self.canvas.pack()

        self.canvas.delete("all")
        font = tkFont.Font(family='Mono', size=15)

        # 绘制ER图
        from pdm_parser import parse_pdm
        ox, oy = 5, 5
        x, y = ox, oy
        my = 0
        padding = 10
        tables = parse_pdm("/Users/liyilin/Workspace/doc/company/AIFactory-train-doc/06 数据模型/deepminer-v2(1).pdm")
        for table in tables:
            tr = TableRect(self.canvas, x, y, table, font)
            if tr.x + tr.width > 1024:
                x = ox
                y = my + padding
                my = 0
                tr = TableRect(self.canvas, x, y, table, font)
            tr.render()
            my = max(my, tr.y + tr.height)
            x += tr.width + padding

        # 绑定事件
        self.canvas.bind("<ButtonPress-1>", lambda e: self.set_cur_pos(e))
        self.canvas.bind("<B1-Motion>", lambda e: self.scroll_canvase(e))
        # self.canvas.
        # self.canvas.bind("<ButtonRelease-1>", lambda event: print("鼠标左键释放"))

    def set_cur_pos(self, event):
        self.cur_pos = (event.x, event.y)
        self.move = [0, 0]

    def scroll_canvase(self, event):
        canvas: tk.Canvas = self.canvas
        xscroll = int((self.cur_pos[0] - event.x + self.move[0]) * self.sensitivity)
        yscroll = int((self.cur_pos[1] - event.y + self.move[1]) * self.sensitivity)
        if math.fabs(xscroll) > 0:
            canvas.xview_scroll(xscroll, tk.UNITS)
            self.move[0] = 0
        else:
            self.move[0] += self.cur_pos[0] - event.x
        if math.fabs(yscroll) > 0:
            canvas.yview_scroll(yscroll, tk.UNITS)
            self.move[1] = 0
        else:
            self.move[1] += self.cur_pos[1] - event.y
        self.cur_pos = (event.x, event.y)


root = tk.Tk()
app = Application(master=root)

app.mainloop()
