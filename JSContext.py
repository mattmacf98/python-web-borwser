import dukpy
from CSSParser import CSSParser
from HTMLParser import HTMLParser
from Utils import tree_to_list

RUNTIME_JS = open("runtime.js").read()
EVENT_DISPATCH_JS = "new Node(dukpy.handle).dispatchEvent(new Event(dukpy.type))"

class JSContext:
    def __init__(self, tab):
        self.tab = tab
        self.node_to_handle = {}
        self.handle_to_node = {}
        self.interp = dukpy.JSInterpreter()
        self.interp.export_function("log", print)
        self.interp.export_function("querySelectorAll", self.querySelectorAll)
        self.interp.export_function("getAttribute", self.getAttribute)
        self.interp.export_function("innerHTML_set", self.innerHTML_set)
        self.interp.evaljs(RUNTIME_JS)

    def querySelectorAll(self, selector_text):
        selector = CSSParser(selector_text).selector()
        nodes = [node for node in tree_to_list(self.tab.root, []) if selector.matches(node)]
        return [self.get_handle(node) for node in nodes]
    
    def getAttribute(self, handle, attr):
        node = self.handle_to_node[handle]
        attr = node.attributes.get(attr, None)
        return attr if attr else ""
    
    def get_handle(self, node):
        if node in self.node_to_handle:
            handle = self.node_to_handle[node]
        else:
            handle = len(self.node_to_handle)
            self.node_to_handle[node] = handle
            self.handle_to_node[handle] = node
        return handle
    
    def dispatch_event(self, type, node):
        handle = self.node_to_handle.get(node, -1)
        do_default = self.interp.evaljs(EVENT_DISPATCH_JS, type=type, handle=handle)
        return not do_default

    def innerHTML_set(self, handle, s):
        doc = HTMLParser("<html><body>" + s + "</body></html>").parse()
        new_nodes = doc.children[0].children
        node = self.handle_to_node[handle]
        node.children = new_nodes
        for child in node.children:
            child.parent = node
        self.tab.render()

    def run(self, script, code):
        try:
            return self.interp.evaljs(code)
        except dukpy.JSRuntimeError as e:
            print("Script", script, "crashed", e)