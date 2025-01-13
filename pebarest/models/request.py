class Request:
    def __init__(self, environ):
        self.method = environ['REQUEST_METHOD']
        self.path = environ['PATH_INFO']
        self.body = environ['BODY']
