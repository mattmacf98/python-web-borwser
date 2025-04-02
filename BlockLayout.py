import tkinter.font
from LineLayout import LineLayout
from Rect import Rect
from Text import Text
from Element import Element
from DrawText import DrawText
from DrawRect import DrawRect
import tkinter

from TextLayout import TextLayout

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
        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.cursor_x = 0

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
        else:
            self.new_line()
            self.recurse(self.node)
            
        for child in self.children:
                child.layout()
        self.height = sum([child.height for child in self.children])

    def recurse(self, tree_node):
        if isinstance(tree_node, Text):
            for word in tree_node.text.split():
                self.word(tree_node, word)
        else:
            for child in tree_node.children:
                self.recurse(child)

    def word(self, tree_node, word):
        color = tree_node.style["color"]
        weight= tree_node.style["font-weight"]
        style = tree_node.style["font-style"]
        if style == "normal":
            style = "roman"
        size = int(float(tree_node.style["font-size"][:-2]) * 0.75)
        font = get_font(size, weight, style)
        width = font.measure(word)
        if self.cursor_x + width > self.width:
            self.new_line()
        line = self.children[-1]
        previous_word = line.children[-1] if line.children else None
        text = TextLayout(tree_node, word, line, previous_word)
        line.children.append(text)
        self.cursor_x += width + font.measure(" ")

    def new_line(self):
        self.cursor_x = 0
        last_line = self.children[-1] if self.children else None
        new_line = LineLayout(self.node, self, last_line)
        self.children.append(new_line)
    
    def paint(self):
        cmds = []
        if self.layout_mode() == "inline":
            if isinstance(self.node, Element):
                bg_color = self.node.style.get("background-color", "transparent")
                if bg_color != "transparent":
                    x2, y2 = self.x + self.width, self.y + self.height
                    cmds.append(DrawRect(Rect(self.x, self.y, x2, y2), bg_color))
        return cmds