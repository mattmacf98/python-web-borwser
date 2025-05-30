LISTENERS = {}
SET_TIMEOUT_REQUESTS = {}
XHR_REQUESTS = {}
RAF_LISTENERS = [];

console = {log: function(x) {call_python("log", x)}}
document = {querySelectorAll: function(s) {
    var handles = call_python("querySelectorAll", s)
    return handles.map(function(h) { return new Node(h)})
}}

function requestAnimationFrame(fn) {
    RAF_LISTENERS.push(fn);
    call_python("requestAnimationFrame");
}

function setTimeout(callback, time_delta) {
    var handle = Object.keys(SET_TIMEOUT_REQUESTS).length;
    SET_TIMEOUT_REQUESTS[handle] = callback;
    call_python("setTimeout", handle, time_delta);
}

function __runSetTimeout(handle) {
    callback = SET_TIMEOUT_REQUESTS[handle];
    callback();
}

function __runXHROnload(body, handle) {
    var obj = XHR_REQUESTS[handle]
    var evt = new Event('load')
    obj.responseText = body
    if (obj.onLoad) {
        obj.onLoad(evt)
    }
}

function __runRAFHandlers() {
    var handlers_copy = RAF_LISTENERS;
    RAF_LISTENERS = [];
    for (var i = 0; i < handlers_copy.length; i++) {
        handlers_copy[i]();
    }
}

function Node(handle) {this.handle = handle;}
Node.prototype.getAttribute = function(attr) {
    return call_python("getAttribute", this.handle, attr)
}
Node.prototype.addEventListener = function(type, listener) {
    // get listeners on this node
    if (!LISTENERS[this.handle]) {
        LISTENERS[this.handle] = {}
    }
    
    // get listeners on this node of the type we want to add
    var listenersDict = LISTENERS[this.handle]
    if (!listenersDict[type]) {
        listenersDict[type] = [];
    }

    // add this type of listener to the node
    var listenerTypeList = listenersDict[type];
    listenerTypeList.push(listener)
}
Node.prototype.dispatchEvent = function(evt) {
    var type = evt.type
    var handle = this.handle;
    var listeners = (LISTENERS[handle] && LISTENERS[handle][type]) || [];
    for (var i = 0; i < listeners.length; i++) {
        listeners[i].call(this, evt);
    }

    return evt.do_default
}

Object.defineProperty(Node.prototype, 'innerHTML', {
    set: function(s) {
        call_python("innerHTML_set", this.handle, s.toString());
    }
});

function Event(type) {
    this.type = type;
    this.do_default = true
}

Event.prototype.preventDefault = function() {
    this.do_default = false
}

function XMLHttpRequest() {
    this.handle = Object.keys(XHR_REQUESTS).length;
    XHR_REQUESTS[this.handle] = this;
}

XMLHttpRequest.prototype.open = function(method, url, is_async) {
    this.is_async = is_async
    this.method = method
    this.url = url
}

XMLHttpRequest.prototype.send = function(body) {
    this.responseText = call_python("XMLHttpRequest_send", this.method, this.url, body, this.is_async, this.handle)
}
