import json
import io


class TestResponse:
    def __init__(self, status: str, headers: list, body: bytes):
        self.status = status
        self.headers = dict(headers)
        self.body = body

    @property
    def status_code(self) -> int:
        return int(self.status.split(' ')[0])

    @property
    def text(self) -> str:
        return self.body.decode('utf-8')

    def json(self):
        return json.loads(self.text)


class TestClient:
    def __init__(self, app):
        self.app = app

    def request(self, method, path, headers=None, body=None, json_data=None):
        if headers is None:
            headers = {}

        body_bytes = b""
        if json_data is not None:
            body_bytes = json.dumps(json_data).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        elif body is not None:
            if isinstance(body, str):
                body_bytes = body.encode('utf-8')
            else:
                body_bytes = body

        environ = {
            'REQUEST_METHOD': method.upper(),
            'PATH_INFO': path,
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '80',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': io.BytesIO(body_bytes),
            'wsgi.errors': io.StringIO(),
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'CONTENT_LENGTH': str(len(body_bytes)),
            'QUERY_STRING': ''
        }

        for k, v in headers.items():
            key = 'HTTP_' + k.upper().replace('-', '_')
            environ[key] = v

        captured_status = []
        captured_headers = []

        def start_response(status, response_headers, exc_info=None):
            captured_status.append(status)
            captured_headers.extend(response_headers)
            return lambda x: None

        response_iter = self.app(environ, start_response)
        response_body = b"".join(response_iter)

        return TestResponse(captured_status[0], captured_headers, response_body)

    def get(self, path, headers=None):
        return self.request('get', path, headers=headers)

    def post(self, path, json=None, headers=None):
        return self.request('post', path, json_data=json, headers=headers)

    def put(self, path, json=None, headers=None):
        return self.request('put', path, json_data=json, headers=headers)

    def delete(self, path, headers=None):
        return self.request('delete', path, headers=headers)

    def patch(self, path, json=None, headers=None):
        return self.request('patch', path, json_data=json, headers=headers)
