from CSSParser import CSSParser, cascade_priority, style
from Element import Element
from HTMLParser import HTMLParser
from DocumentLayout import DocumentLayout
from Text import Text
from Utils import HEIGHT, paint_tree, tree_to_list

HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

DEFAULT_STYLE_SHEET = CSSParser(open("browser.css").read()).parse()

class Tab:
    def __init__(self, tab_height) -> None:
        self.history = []
        self.scroll = 0
        self.url = None
        self.tab_height = tab_height

    def click(self, x, y):
         # get screen coords -> convert to web page coords
         y += self.scroll

          # get all layout objects that contain the click
         objs = [obj for obj in tree_to_list(self.document, []) if obj.x <= x and obj.x + obj.width > x and obj.y <= y and obj.y + obj.height > y]
         if not objs: return
         # get the last painted element (i.e. top element)
         element = objs[-1].node

         # crawl up tree to find the link element
         while element:
              if isinstance(element, Text):
                   pass
              elif element.tag == "a" and "href" in element.attributes:
                    url = self.url.resolve(element.attributes["href"])
                    return self.load(url)
              element = element.parent

    def scrolldown(self):
         max_y = max(self.document.height + 2*VSTEP - self.tab_height, 0)
         self.scroll = min(self.scroll + SCROLL_STEP, max_y)

    def scrollUp(self):
         self.scroll -= SCROLL_STEP

    def draw(self, canvas, offset):
         for cmd in self.display_cmds:
              if cmd.top > self.scroll + HEIGHT or cmd.bottom < self.scroll: continue
              cmd.execute(self.scroll - offset, canvas)

    def go_back(self):
         if len(self.history) > 1:
              self.history.pop() # remove current url
              back_url = self.history.pop()
              self.load(back_url)
              
    def load(self, url):
        self.url = url
        self.history.append(self.url)
        body = url.request()
        root = HTMLParser(body).parse()
        
        rules = DEFAULT_STYLE_SHEET.copy()
        links = [node.attributes["href"] for node in tree_to_list(root, []) if isinstance(node, Element) 
                 and node.tag == "link" and node.attributes.get("rel") == "stylesheet" and 'href' in node.attributes]
        for link in links:
             style_url = url.resolve(link)
             try:
                  body = style_url.request()
             except:
                  continue
             rules.extend(CSSParser(body).parse())
        
        style(root, sorted(rules, key=cascade_priority))
        self.document = DocumentLayout(root)
        self.document.layout()
        self.display_cmds = []
        paint_tree(self.document, self.display_cmds)