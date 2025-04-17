import socket
import ssl

COOKIE_JAR = {}

class URL:
    def __str__(self):
        port_part = ":" + str(self.port)
        if self.scheme == "https" and self.port == 443:
            port_part = ""
        elif self.scheme == "http" and self.port == 80:
            port_part = ""
        return self.scheme + "://" + self.host + port_part + self.path
    
    def __init__(self, url: str):
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"]

        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url

        # figure out correct port
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    def origin(self):
        return self.scheme + "://" + self.host + ":" + str(self.port)

    def request(self, referer, payload=None):
        sckt = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )

        sckt.connect((self.host, self.port))
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            sckt = ctx.wrap_socket(sckt, server_hostname=self.host)

        method = "POST" if payload else "GET"

        # Send the request to the host
        request = "{} {} HTTP/1.0\r\n".format(method, self.path)
        request += "Host: {}\r\n".format(self.host)
        if payload:
            length = len(payload.encode("utf8"))
            request += "Content-Length: {}\r\n".format(length)
        if self.host in COOKIE_JAR:
            cookie, params = COOKIE_JAR[self.host]
            allow_cookie = True
            if referer and params.get("samesite", "none") == "lax":
                if method != "GET":
                    allow_cookie = self.host == referer.host
            if allow_cookie:
                request += "Cookie: {}\r\n".format(cookie)
        request += "\r\n"

        if payload:
            request += payload

        sckt.send(request.encode("utf8"))

        # get the response
        response = sckt.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        # extract headers
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        if "set-cookie" in response_headers:
            cookie = response_headers["set-cookie"]
            params = {}
            if ";" in cookie:
                cookie, rest = cookie.split(";", 1)
                for param in rest.split(";"):
                    if "=" in param:
                        key, value = param.split("=", 1)
                    else:
                        value = "true"
                    params[key.strip().casefold()] = value.strip().casefold()
            COOKIE_JAR[self.host] = (cookie, params)

        #get actual content
        content = response.read()
        sckt.close()

        return response_headers, content
    
    def resolve(self, url):
        if "://" in url: return URL(url)
        if not url.startswith("/"):
            dir, _ = self.path.rsplit("/", 1)
            while url.startswith("../"):
                _, url = url.split("/", 1)
                if "/" in dir:
                    dir, _ = dir.rsplit("/", 1)
            url = dir + "/" + url
        return URL(self.scheme + "://" + self.host + ":" + str(self.port) + url)