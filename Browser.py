import tkinter
from HTMLParser import HTMLParser
from DocumentLayout import DocumentLayout
from Utils import paint_tree

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

class Browser:
    def __init__(self) -> None:
        self.scroll = 0
        self.window = tkinter.Tk()
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollUp)
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()

    def scrolldown(self, e):
         max_y = max(self.document.height + 2*VSTEP - HEIGHT, 0)
         self.scroll = min(self.scroll + SCROLL_STEP, max_y)
         self.draw()

    def scrollUp(self, e):
         self.scroll -= SCROLL_STEP
         self.draw()

    def draw(self):
         self.canvas.delete("all")
         for cmd in self.display_cmds:
              if cmd.top > self.scroll + HEIGHT or cmd.bottom < self.scroll: continue
              cmd.execute(self.scroll, self.canvas)
              
    def load(self, url):
        body = url.request()
        root = HTMLParser(body).parse()
        self.document = DocumentLayout(root)
        self.document.layout()
        self.display_cmds = []
        paint_tree(self.document, self.display_cmds)
        self.draw()