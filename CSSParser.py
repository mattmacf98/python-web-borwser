from DescendantSelector import DescendantSelector
from Element import Element
from TagSelector import TagSelector

INHERITED_PROPERTIES = {
    "font-size": "16px",
    "font-style": "normal",
    "font-weight": "normal",
    "color": "black",
}

class CSSParser:
    def __init__(self, style_string):
        self.style_string = style_string
        self.index = 0

    def whitespace(self):
        while self.index < len(self.style_string) and self.style_string[self.index].isspace():
            self.index += 1

    def selector(self):
        out = TagSelector(self.word().casefold())
        self.whitespace()
        while self.index < len(self.style_string) and self.style_string[self.index] != "{":
            tag = self.word().casefold()
            descendant = TagSelector(tag.casefold())
            out = DescendantSelector(out, descendant)
            self.whitespace()
        return out
    
    def word(self):
        start = self.index
        while self.index < len(self.style_string):
            if self.style_string[self.index].isalnum() or self.style_string[self.index] in "#-.%":
                self.index += 1
            else: 
                break
        
        if self.index <= start:
            raise Exception(f"Parse error: {self.index} is less than or equal to start {start}")
        return self.style_string[start:self.index]

    def literal(self, literal):
        if self.index >= len(self.style_string) or self.style_string[self.index] != literal:
            raise Exception(f"Parse error: {self.index} is out of bounds or {self.style_string[self.index]} is not {literal}")
        self.index += 1

    def pair(self):
        property = self.word()
        self.whitespace()
        self.literal(":")
        self.whitespace()
        value = self.word()
        return property.casefold(), value
    
    def body(self):
        pairs = {}
        while self.index < len(self.style_string) and self.style_string[self.index] != "}":
            try:
                property, value = self.pair()
                pairs[property] = value
                self.whitespace()
                self.literal(";")
                self.whitespace()
            except:
                why = self.ignore_until([";", "}"])
                if why == ";":
                    self.literal(";")
                    self.whitespace()
                else:
                    break
            
        return pairs
    
    def ignore_until(self, chars):
        while self.index < len(self.style_string):
            if self.style_string[self.index] in chars:
                return self.style_string[self.index]
            else:
                self.index += 1
        return None
    
    def parse(self):
        rules = []
        while self.index < len(self.style_string):
            try:
                self.whitespace()
                selector = self.selector()
                self.literal("{")
                self.whitespace()
                body = self.body()
                self.literal("}")
                rules.append((selector, body))
            except Exception:
                why = self.ignore_until(["}"])
                if why == "}":
                    self.literal("}")
                    self.whitespace()
                else:
                    break
        return rules

    
def style(node, rules):
    node.style = {}

    # Inherit properties from parent or default value
    for property, default_value in INHERITED_PROPERTIES.items():
        if node.parent:
            node.style[property] = node.parent.style[property]
        else: 
            node.style[property] = default_value
    # apply css rules from a file
    for selector, body in rules:
        if not selector.matches(node): continue
        for property, value in body.items():
            node.style[property] = value

    # apply inline styles
    if isinstance(node, Element) and "style" in node.attributes:
        pairs = CSSParser(node.attributes["style"]).body()
        for property, value in pairs.items():
            node.style[property] = value

    # resolve percentage font-size
    if node.style["font-size"].endswith("%"):
        if node.parent:
            parent_font_size = node.parent.style["font-size"]
        else:
            parent_font_size = INHERITED_PROPERTIES["font-size"]
        node_pct = float(node.style["font-size"][:-1]) / 100
        parent_px = float(parent_font_size[:-2])
        node.style["font-size"] = f"{parent_px * node_pct}px"

    # recurse on children to style them
    for child in node.children:
        style(child, rules)

def cascade_priority(rule):
    selector, body = rule
    return selector.priority