import dukpy
from CSSParser import CSSParser
from HTMLParser import HTMLParser
from Task import Task
from Utils import tree_to_list
import threading


RUNTIME_JS = open("runtime.js").read()
EVENT_DISPATCH_JS = "new Node(dukpy.handle).dispatchEvent(new Event(dukpy.type))"
SETTIMEOUT_JS = "__runSetTimeout(dukpy.handle)"
XHR_ONLOAD = "__runXHROnLoad(dukpy.out, dukpy.handle)"

class JSContext:
    def __init__(self, tab):
        self.tab = tab
        self.node_to_handle = {}
        self.handle_to_node = {}
        self.discarded = False
        self.interp = dukpy.JSInterpreter()
        self.interp.export_function("log", print)
        self.interp.export_function("querySelectorAll", self.querySelectorAll)
        self.interp.export_function("getAttribute", self.getAttribute)
        self.interp.export_function("innerHTML_set", self.innerHTML_set)
        self.interp.export_function("setTimeout", self.setTimeout)
        self.interp.export_function("requestAnimationFrame", self.requestAnimationFrame)
        self.tab.browser.measure.time("JSContext")
        self.interp.evaljs(RUNTIME_JS)
        self.tab.browser.measure.stop("JSContext")

    def requestAnimationFrame(self):
        self.tab.set_needs_render()
        self.tab.browser.set_needs_animation_frame(self.tab)

    def querySelectorAll(self, selector_text):
        selector = CSSParser(selector_text).selector()
        nodes = [node for node in tree_to_list(self.tab.root, []) if selector.matches(node)]
        return [self.get_handle(node) for node in nodes]
    
    def getAttribute(self, handle, attr):
        node = self.handle_to_node[handle]
        attr = node.attributes.get(attr, None)
        return attr if attr else ""
    
    def dispatch_settimeout(self, handle):
        if self.discarded:
            return
        self.tab.browser.measure.time("setTimeout")
        self.interp.evaljs(SETTIMEOUT_JS, handle=handle)
        self.tab.browser.measure.stop("setTimeout")
    
    def setTimeout(self, handle, time_delta):
        def run_callback():
            task = Task(self.dispatch_settimeout, handle)
            self.tab.task_runner.scheduele_task(task)
        threading.Timer(time_delta / 1000.0, run_callback).start()

    
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
        self.tab.browser.measure.time("dispatchEvent")
        do_default = self.interp.evaljs(EVENT_DISPATCH_JS, type=type, handle=handle)
        self.tab.browser.measure.stop("dispatchEvent")
        return not do_default

    def innerHTML_set(self, handle, s):
        doc = HTMLParser("<html><body>" + s + "</body></html>").parse()
        new_nodes = doc.children[0].children
        node = self.handle_to_node[handle]
        node.children = new_nodes
        for child in node.children:
            child.parent = node
        self.tab.set_needs_render()
        self.tab.render()

    def XMLHttpRequest_send(self, method, url, body, is_async, handle):
        full_url = self.tab.url.resolve(url)
        if not self.tab.allowed_request(full_url):
            raise Exception("Blocked request to {} due to CSP".format(full_url))
        if full_url.origin() != self.tab.url.origin():
            raise Exception("Cross-origin XHR request not allowed")
        
        def run_load():
            headers, out = full_url.request(self.tab.url, body)
            task = Task(self.dispatch_xhr_onload, out, handle)
            self.tab.task_runner.scheduele_task(task)
            return out
        
        if not is_async:
            return run_load()
        else:
            threading.Thread(target=run_load).start()
    
    def dispatch_xhr_onload(self, out, handle):
        if self.discarded:
            return
        self.tab.browser.measure.time("xhr_onload")
        do_default = self.interp.evaljs(XHR_ONLOAD, out=out, handle=handle)
        self.tab.browser.measure.stop("xhr_onload")
        return not do_default

    def run(self, script, code):
        try:
            return self.interp.evaljs(code)
        except dukpy.JSRuntimeError as e:
            print("Script", script, "crashed", e)