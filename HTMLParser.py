from Element import Element
from Text import Text


SELF_CLOSING_TAGS = [
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr"
]

class HTMLParser:
    def __init__(self, body):
        self.body = body
        self.unfinished = []
    
    def parse(self):
        text = ""
        in_tag = False
        for char in self.body:
            if char == "<":
                in_tag = True
                if text: 
                    self.add_text(text)
                text = ""
            elif char == ">":
                in_tag = False
                self.add_tag(text)
                text = ""
            else:
                text += char
        
        if not in_tag and text:
            self.add_text(text)
        return self.finish()
    
    def add_text(self, text):
        if text.isspace(): return
        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)

    def add_tag(self, tag):
        if tag.startswith("!"): return

        tag, attributes = self.get_attributes(tag)

        if tag.startswith("/"):
            if len(self.unfinished) == 1: return
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        elif tag in SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            node = Element(tag, attributes, parent)
            parent.children.append(node)
        else:
            parent = self.unfinished[-1] if self.unfinished else None
            node = Element(tag, attributes, parent)
            self.unfinished.append(node)

    def finish(self):
        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent =  self.unfinished[-1]
            parent.children.append(node)
        return self.unfinished.pop()
    
    def get_attributes(self, text):
        parts = text.split()
        tag = parts[0].casefold()
        attributes = {}
        for attrpair in parts[1:]:
            if "=" in attrpair:
                key, value = attrpair.split("=",1)
                if len(value) > 2 and value[0] in ["'", "\""]:
                    value = value[1:-1]
                attributes[key.casefold()] = value
            else:
                attributes[attrpair.casefold()] = ""
        return tag, attributes