import skia
from Utils import parse_color

class DrawRect:
    def __init__(self, rect, radius, color):
        self.rect = rect
        self.rrect = skia.RRect.MakeRectXY(rect, radius, radius)
        self.top = rect.top()
        self.left = rect.left()
        self.bottom = rect.bottom()
        self.right = rect.right()
        self.color = color
        self.radius = radius

    def execute(self, canvas):
        paint = skia.Paint(Color=parse_color(self.color))
        canvas.drawRRect(self.rrect, paint)