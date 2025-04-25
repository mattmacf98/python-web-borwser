
from DrawText import DrawText
from Utils import get_font, linespace


class TextLayout:
    def __init__(self, node, word, parent, previous):
        self.node = node
        self.word = word
        self.children = []
        self.parent = parent
        self.previous = previous
        self.x = None
        self.y = None
        self.width = None
        self.height = None

    def layout(self):
        weight= self.node.style["font-weight"]
        style = self.node.style["font-style"]
        if style == "normal":
            style = "roman"
        size = int(float(self.node.style["font-size"][:-2]) * 0.75)
        self.font = get_font(size, weight, style)

        self.width = self.font.measureText(self.word)
        if self.previous:
            space = self.previous.font.measureText(" ")
            self.x = self.previous.x + self.previous.width + space
        else:
            self.x = self.parent.x
        
        self.height = linespace(self.font)
    
    def should_paint(self):
        return True

    def paint_effects(self, cmds):
        return cmds
    
    def paint(self):
        color = self.node.style["color"]
        return [DrawText(self.x, self.y, self.word, self.font, color)]