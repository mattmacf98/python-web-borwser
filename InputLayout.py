
import tkinter

from DrawLine import DrawLine
from DrawRect import DrawRect
from DrawText import DrawText
from Rect import Rect
from Utils import get_font
from Text import Text

INPUT_WIDTH_PX = 200

class InputLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.children = []
        self.parent = parent
        self.previous = previous
        self.x = None
        self.y = None
        self.width = INPUT_WIDTH_PX
        self.height = None

    def layout(self):
        weight= self.node.style["font-weight"]
        style = self.node.style["font-style"]
        if style == "normal":
            style = "roman"
        size = int(float(self.node.style["font-size"][:-2]) * 0.75)
        self.font = get_font(size, weight, style)

        if self.previous:
            space = self.previous.font.measure(" ")
            self.x = self.previous.x + self.previous.width + space
        else:
            self.x = self.parent.x
        
        self.height = self.font.metrics("linespace")

    def should_paint(self):
        return True

    def paint(self):
        cmds = []

        bgColor = self.node.style.get("background-color", "transparent")
        if bgColor != "transparent":
            rect = DrawRect(Rect(self.x, self.y, self.x + self.width, self.y + self.height), bgColor)
            cmds.append(rect)

        if self.node.tag == "input":
            text = self.node.attributes.get("value", "")
        elif self.node.tag == "button":
            if len(self.node.children) == 1 and isinstance(self.node.children[0], Text):
                text = self.node.children[0].text
            else:
                print("Ignoring HTML contents inside button")
                text = ""
        color = self.node.style["color"]
        cmds.append(DrawText(self.x, self.y, text, self.font, color))

        if self.node.is_focused:
            cx = self.x + self.font.measure(text)
            cmds.append(DrawLine(cx, self.y, cx, self.y + self.height, "black", 1))

        return cmds