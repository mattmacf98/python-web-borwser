class Text:
    def __init__(self, text, parent):
        self.text = text
        self.children = []
        self.parent = parent
        self.is_focused = False

    def __repr__(self):
        return repr(self.text)