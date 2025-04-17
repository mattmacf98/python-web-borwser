import socket
import urllib
import urllib.parse
import random
import html

ENTRIES = [("Matthew was here", "matthew")]
SESSIONS = {}
LOGINS = {
    "matthew": "password",
    "admin": "password"
}

def show_comments(session):
    out = "<!doctype html>"
    for entry, who in ENTRIES:
        out += "<p>" + html.escape(entry) + "\n <i>by " + html.escape(who) + "</i></p>"

    if "user" in session:
        nonce = str(random.random())[2:]
        session["nonce"] = nonce
        out += "<h1> Hello, {}!</h1>".format(session["user"])
        out += "<form action=add method=post>"
        out += "<p><input name=guest></p>"
        out += "<input type=hidden name=nonce value={}>".format(nonce)
        out += "<p><button>Sign the book!</button></p>"
        out += "</form>"
        out += "<strong></strong>"
        out += "<script src=\"/comment.js\"></script>"
    else:
        out += "<p><a href=/login>Log in</a></p>"

    return "200 OK", out

def login_form(session):
    body = "<!doctype html>"
    body += "<form action=/ method=post>"
    body += "<p>Username: <input name=username></p>"
    body += "<p>Password: <input name=password type=password></p>"
    body += "<p><button>Log in</button></p>"
    body += "</form>"
    return "200 OK", body

def form_decode(body):
    params = {}
    for field in body.split("&"):
        name, value = field.split("=", 1)
        name = urllib.parse.unquote_plus(name)
        value = urllib.parse.unquote_plus(value)
        params[name] = value
    return params

def add_entry(session, params):
    if "nonce" not in session or "nonce" not in params:
        return "401 Unauthorized", "<h1>Adding comments requires login</h1>"
    if session["nonce"] != params["nonce"]:
        return "401 Unauthorized", "<h1>Adding comments requires login</h1>"
    if "user" not in session: 
        return "401 Unauthorized", "<h1>Adding comments requires login</h1>"
    if 'guest' in params and len(params['guest']) <= 20:
        ENTRIES.append((params['guest'], session['user']))
    return show_comments(session)

def do_login(session, params):
    username = params.get("username")
    password = params.get("password")
    if username in LOGINS and LOGINS[username] == password:
        session["user"] = username
        return show_comments(session)
    else:
        out = "<!doctype html>"
        out += "<h1>Login failed</h1>"
        out += "<p>Invalid username or password</p>"
        return "401 Unauthorized", out

def not_found(url, method):
    out = "<!doctype html>"
    out += "<h1>{} {} not found!</h1>".format(method, url)
    return out

def do_request(session, method, url, headers, body):
    if method == "GET" and url == "/":
        return show_comments(session)
    elif method == "GET" and url == "/login":
        return login_form(session)
    elif method == "GET" and url == "/comment.js":
        with open("comment.js") as f:
            return "200 OK", f.read()
    elif method == "GET" and url == "/comment.css":
        with open("comment.css") as f:
            return "200 OK", f.read()
    elif method == "POST" and url == "/":
        params = form_decode(body)
        return do_login(session, params)
    elif method == "POST" and url == "/add":
        params = form_decode(body)
        return add_entry(session, params)
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

    if "cookie" in headers:
        token = headers["cookie"][len("token="):]
    else:
        token = str(random.random())[2:]


    session = SESSIONS.setdefault(token, {})
    status, body = do_request(session, method, url, headers, body)

    response = "HTTP/1.0 {}\r\n".format(status)
    response += "Content-Length: {}\r\n".format(len(body.encode("utf8")))
    csp = "default-src http://localhost:8000"
    response += "Content-Security-Policy: {}\r\n".format(csp)
    if "cookie" not in headers:
        response += "Set-Cookie: token={}; SameSite=Lax\r\n".format(token)
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

