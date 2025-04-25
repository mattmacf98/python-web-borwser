import skia
from Utils import parse_color

class DrawOutline:
    def __init__(self, rect, color, thickness):
        self.rect = rect
        self.color = color
        self.thickness = thickness

    def execute(self, canvas):
        paint = skia.Paint(Color=parse_color(self.color), StrokeWidth=self.thickness, Style=skia.Paint.kStroke_Style)
        canvas.drawRect(self.rect, paint)