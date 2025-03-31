import tkinter.font
from Text import Text
from Element import Element
from DrawText import DrawText
from DrawRect import DrawRect
import tkinter

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
FONTS = {}
BLOCK_ELEMENTS = ["html", "body", "article", "section", "nav", "aside", "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
                   "footer", "address", "p", "hr", "pre", "blockquote", "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure", 
                   "figcaption", "main", "div", "table", "form", "fieldset", "legend", "details", "summary"]

def get_font(size, weight, style):
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight, slant=style)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]

class BlockLayout:
    def __init__(self, node, parent, previous_sibling):
        self.node = node
        self.parent = parent
        self.previous_sibling = previous_sibling
        self.children = []
        self.display_list = []
        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.cursor_x = 0
        self.cursor_y = 0

    def layout_mode(self):
        if isinstance(self.node, Text):
            return "inline"
        elif any([isinstance(child, Element) and child.tag in BLOCK_ELEMENTS for child in self.node.children]):
            return "block"
        elif self.node.children:
            return "inline"
        else:
            return "block"
    
    def layout(self):
        self.x = self.parent.x
        self.width = self.parent.width
        if self.previous_sibling:
            self.y = self.previous_sibling.y + self.previous_sibling.height
        else:
            self.y = self.parent.y

        mode = self.layout_mode()
        if mode == "block":
            previous = None
            for child in self.node.children:
                next = BlockLayout(child, self, previous)
                self.children.append(next)
                previous = next
            for child in self.children:
                child.layout()
            self.height = sum([child.height for child in self.children])
        else:
            self.cursor_x = 0
            self.cursor_y = 0

            self.weight = "normal"
            self.style = "roman"
            self.size = 12

            self.line = []
            self.recurse(self.node)
            self.flush()
            self.height = self.cursor_y

    def open_tag(self, tag):
        if tag == "i":
            self.style = "italic"
        elif tag == "b":
            self.weight = "bold"
        elif tag == "small":
            self.size -= 2
        elif tag == "big":
            self.size += 4
        elif tag == "br":
            self.flush()

    def close_tag(self, tag):
        if tag == "i":
            self.style = "roman"
        elif tag == "b":
            self.weight = "normal"
        elif tag == "small":
            self.size += 2  
        elif tag == "big":
            self.size -= 4
        elif tag == "p":
            self.flush()
            self.cursor_y += VSTEP

    def recurse(self, tree_node):
        if isinstance(tree_node, Text):
            for word in tree_node.text.split():
                self.word(word)
        else:
            self.open_tag(tree_node.tag)
            for child in tree_node.children:
                self.recurse(child)
            self.close_tag(tree_node.tag)

    def word(self, word):
        font = get_font(self.size, self.weight, self.style)
        width = font.measure(word)
        if self.cursor_x + width > self.width:
            self.flush()
        self.line.append((self.cursor_x, word, font))
        self.cursor_x += width + font.measure(" ")

    def flush(self):
        if not self.line: return
        metrics = [font.metrics() for x, word, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent
        for relative_x, word, font in self.line:
            x = self.x + relative_x
            y = self.y + baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = 0
        self.line = []
    
    def paint(self):
        cmds = []
        if self.layout_mode() == "inline":
            if isinstance(self.node, Element) and self.node.tag == "pre":
                x2, y2 = self.x + self.width, self.y + self.height
                cmds.append(DrawRect(self.x, self.y, x2, y2, "gray"))
            for x, y, word, font in self.display_list:
                cmds.append(DrawText(x, y, word, font))
        return cmds