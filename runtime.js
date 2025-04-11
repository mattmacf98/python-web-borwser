LISTENERS = {}

console = {log: function(x) {call_python("log", x)}}
document = {querySelectorAll: function(s) {
    var handles = call_python("querySelectorAll", s)
    return handles.map(function(h) { return new Node(h)})
}}

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