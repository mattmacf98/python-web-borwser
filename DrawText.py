import skia

from Utils import parse_color, linespace

class DrawText:
    def __init__(self, x1, y1, text, font, color):
        self.rect = skia.Rect.MakeLTRB(x1, y1, x1 + font.measureText(text), y1 - font.getMetrics().fAscent + font.getMetrics().fDescent)
        self.top = y1
        self.left = x1
        self.text = text
        self.font = font
        self.bottom = self.top + linespace(self.font)
        self.color = color
    
    def execute(self, canvas):
        paint = skia.Paint(AntiAlias=True, Color=parse_color(self.color))
        baseline = self.top - self.font.getMetrics().fAscent
        canvas.drawString(self.text, float(self.left), baseline, self.font, paint)