from Text import Text
from Tag import Tag

def lex(body: str):
    out = []
    buffer = ""
    in_tag = False
    for char in body:
        if char == "<":
            in_tag = True
            if buffer:
                out.append(Text(buffer))
            buffer = ""
        elif char == ">":
            in_tag = False
            out.append(Tag(buffer))
            buffer = ""
        else:
            buffer += char
    if not in_tag and buffer:
        out.append(Text(buffer))
    return out