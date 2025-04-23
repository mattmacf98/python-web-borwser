import urllib.parse
from CSSParser import CSSParser, cascade_priority, style
from Element import Element
from HTMLParser import HTMLParser
from DocumentLayout import DocumentLayout
from JSContext import JSContext
from Text import Text
from URL import URL
from Utils import HEIGHT, tree_to_list
from PaintUtils import paint_tree
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
                    if self.js.dispatch_event("click", element):
                         return
                    url = self.url.resolve(element.attributes["href"])
                    return self.load(url)
              elif element.tag == "input":
                   if self.js.dispatch_event("click", element):
                        return
                   self.focus = element
                   element.attributes["value"] = ""
                   self.focus = element
                   element.is_focused = True
                   return self.render()
              elif element.tag == "button":
                   if self.js.dispatch_event("click", element):
                        return
                   # walkl up tree to fins form for this button
                   while element:
                        if element.tag == "form" and "action" in element.attributes:
                             return self.submit_form(element)
                        element = element.parent
                             
              element = element.parent
          
         self.render()

    def submit_form(self, element):
         if self.js.dispatch_event("submit", element):
              return
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
              if self.js.dispatch_event("keydown", self.focus):
                   return
              self.focus.attributes["value"] += char
              self.render() 

    def scrolldown(self):
         max_y = max(self.document.height + 2*VSTEP - self.tab_height, 0)
         self.scroll = min(self.scroll + SCROLL_STEP, max_y)

    def scrollUp(self):
         self.scroll -= SCROLL_STEP

    def raster(self, canvas):
         for cmd in self.display_cmds:
              cmd.execute(canvas)

    def go_back(self):
         if len(self.history) > 1:
              self.history.pop() # remove current url
              back_url = self.history.pop()
              self.load(back_url)

    def allowed_request(self, url):
         return self.allowed_origins == None or url.origin() in self.allowed_origins
              
    def load(self, url, payload=None):
        self.url = url
        self.history.append(self.url)
        headers, body = url.request(self.url, payload)
        
        self.allowed_origins = None
        if "content-security-policy" in headers:
             csp = headers["content-security-policy"].split()
             if len(csp) > 0 and csp[0] == "default-src":
                  self.allowed_origins = []
                  for origin in csp[1:]:
                       self.allowed_origins.append(URL(origin).origin())

        self.root = HTMLParser(body).parse()
        
        self.rules = DEFAULT_STYLE_SHEET.copy()
     #    retrieve and apply css files
        links = [node.attributes["href"] for node in tree_to_list(self.root, []) if isinstance(node, Element) 
                 and node.tag == "link" and node.attributes.get("rel") == "stylesheet" and 'href' in node.attributes]
        for link in links:
             style_url = url.resolve(link)
             if not self.allowed_request(style_url):
                  print("Blocked request to {} due to CSP".format(style_url))
                  continue
             try:
                  headers, body = style_url.request(url)
             except:
                  continue
             self.rules.extend(CSSParser(body).parse())

          # retrieve and execute js scripts
        self.js = JSContext(self)
        scripts = [node.attributes["src"] for node in tree_to_list(self.root, []) if isinstance(node, Element)
                   and node.tag == "script" and "src" in node.attributes]     
        for script in scripts:
             script_url = url.resolve(script)
             if not self.allowed_request(script_url):
                  print("Blocked request to {} due to CSP".format(script_url))
                  continue
             try:
                  headers, body = script_url.request(url)
             except:
                  continue
             self.js.run(script, body)
        self.render()
     
    def render(self):
        style(self.root, sorted(self.rules, key=cascade_priority))
        self.document = DocumentLayout(self.root)
        self.document.layout()
        self.display_cmds = []
        paint_tree(self.document, self.display_cmds)