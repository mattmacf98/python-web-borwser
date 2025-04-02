class DrawRect:
    def __init__(self, rect, color):
        self.top = rect.top
        self.left = rect.left
        self.bottom = rect.bottom
        self.right = rect.right
        self.color = color

    def execute(self, scroll, canvas):
        canvas.create_rectangle(
            self.left, self.top - scroll,
            self.right, self.bottom - scroll,
            width=0,
            fill=self.color)