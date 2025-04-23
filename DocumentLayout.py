from BlockLayout import BlockLayout

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18

class DocumentLayout:
    def __init__(self, root):
        self.root = root
        self.parent = None
        self.children = []   

    def layout(self):
        child = BlockLayout(self.root, self, None)
        self.children.append(child)

        self.x = HSTEP
        self.y = VSTEP
        self.width = WIDTH - 2 * HSTEP
        child.layout()
        self.height = child.height

    def paint_effects(self, cmds):
        return cmds

    def should_paint(self):
        return True
        
    def paint(self):
        return []