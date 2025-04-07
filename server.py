import socket
import urllib
import urllib.parse

ENTRIES = ["Matthew was here"]

def show_comments():
    out = "<!doctype html>"
    for entry in ENTRIES:
        out += "<p>" + entry + "</p>"

    out += "<form action=add method=post>"
    out += "<p><input name=guest></p>"
    out += "<p><button>Sign the book!</button></p>"
    out += "</form>"
    return "200 OK", out

def form_decode(body):
    params = {}
    for field in body.split("&"):
        name, value = field.split("=", 1)
        name = urllib.parse.unquote_plus(name)
        value = urllib.parse.unquote_plus(value)
        params[name] = value
    return params

def add_entry(params):
    if 'guest' in params:
        ENTRIES.append(params['guest'])
    return show_comments()

def not_found(url, method):
    out = "<!doctype html>"
    out += "<h1>{} {} not found!</h1>".format(method, url)
    return out

def do_request(method, url, headers, body):
    if method == "GET" and url == "/":
        return show_comments()
    elif method == "POST" and url == "/add":
        params = form_decode(body)
        return add_entry(params)
    else:
        return "404 Not Found", not_found(url, method)

def handle_connection(connection):
    req = connection.makefile("b")
    req_line = req.readline().decode("utf8")
    method, url, version = req_line.split(" ", 2)
    assert method in ["GET", "POST"]

    headers = {}
    while True:
        line = req.readline().decode("utf8")
        if line == '\r\n': break
        header, value = line.split(":", 1)
        headers[header.casefold()] = value.strip()
    if 'content-length' in headers:
        length = int(headers['content-length'])
        body = req.read(length).decode('utf8')
    else:
        body = None
    status, body = do_request(method, url, headers, body)

    response = "HTTP/1.0 {}\r\n".format(status)
    response += "Content-Length: {}\r\n".format(len(body.encode("utf8")))
    response += "\r\n" + body
    connection.send(response.encode("utf8"))
    connection.close()

if __name__ == "__main__":
    sckt = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_STREAM,
        proto=socket.IPPROTO_TCP
    )
    sckt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sckt.bind(('', 8000))
    sckt.listen()

    while True:
        connection, address = sckt.accept()
        handle_connection(connection)

