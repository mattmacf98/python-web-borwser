import urllib.parse
from CSSParser import CSSParser, cascade_priority, style
from Element import Element
from HTMLParser import HTMLParser
from DocumentLayout import DocumentLayout
from Text import Text
from Utils import HEIGHT, paint_tree, tree_to_list
import urllib

HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

DEFAULT_STYLE_SHEET = CSSParser(open("browser.css").read()).parse()

class Tab:
    def __init__(self, tab_height) -> None:
        self.history = []
        self.scroll = 0
        self.url = None
        self.focus = None
        self.tab_height = tab_height

    def click(self, x, y):
         if self.focus:
              self.focus.is_focused = False
              self.focus = None

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
              elif element.tag == "input":
                   self.focus = element
                   element.attributes["value"] = ""
                   self.focus = element
                   element.is_focused = True
                   return self.render()
              elif element.tag == "button":
                   # walkl up tree to fins form for this button
                   while element:
                        if element.tag == "form" and "action" in element.attributes:
                             return self.submit_form(element)
                        element = element.parent
                             
              element = element.parent
          
         self.render()

    def submit_form(self, element):
         inputs = [node for node in tree_to_list(element, []) if isinstance(node, Element) and node.tag == "input" and "name" in node.attributes]
         
         body = ""
         for input in inputs:
              name = input.attributes["name"]
              value = input.attributes.get("value", "")

              name = urllib.parse.quote(name)
              value = urllib.parse.quote(value)
              body += "&" + name + "=" + value
         body = body[1:]

         url = self.url.resolve(element.attributes["action"])
         self.load(url, body)

    def keypress(self, char):
         if self.focus:
              self.focus.attributes["value"] += char
              self.render() 

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
              
    def load(self, url, payload=None):
        self.url = url
        self.history.append(self.url)
        body = url.request(payload)
        self.root = HTMLParser(body).parse()
        
        self.rules = DEFAULT_STYLE_SHEET.copy()
        links = [node.attributes["href"] for node in tree_to_list(self.root, []) if isinstance(node, Element) 
                 and node.tag == "link" and node.attributes.get("rel") == "stylesheet" and 'href' in node.attributes]
        for link in links:
             style_url = url.resolve(link)
             try:
                  body = style_url.request()
             except:
                  continue
             self.rules.extend(CSSParser(body).parse())
        self.render()
     
    def render(self):
        style(self.root, sorted(self.rules, key=cascade_priority))
        self.document = DocumentLayout(self.root)
        self.document.layout()
        self.display_cmds = []
        paint_tree(self.document, self.display_cmds)