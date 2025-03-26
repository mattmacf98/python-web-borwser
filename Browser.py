import tkinter

from utils import lex

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
         self.scroll += SCROLL_STEP
         self.draw()

    def scrollUp(self, e):
         self.scroll -= SCROLL_STEP
         self.draw()

    def draw(self):
         self.canvas.delete("all")
         for x, y, char in self.display_list:
              if y > self.scroll + HEIGHT or y + VSTEP < self.scroll: continue
              self.canvas.create_text(x, y - self.scroll, text=char)
              
    def load(self, url):
        body = url.request()
        text = lex(body)
        
        self.display_list = layout(text)
        self.draw()

def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for char in text:
        display_list.append((cursor_x, cursor_y, char))
        cursor_x += HSTEP
        if cursor_x >= WIDTH - HSTEP:
                cursor_y += VSTEP
                cursor_x = HSTEP
    return display_list