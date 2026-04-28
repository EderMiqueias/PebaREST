# PebaREST

> A lightweight Python web framework for building REST APIs with simplicity and total control.

PebaREST is a WSGI-based micro-framework built from the ground up as an academic project (TCC — *Trabalho de Conclusão de Curso*). Its philosophy is straightforward: give the developer a clean, transparent request/response cycle with no hidden magic, while keeping the code minimal and readable. No auto-wiring, no black boxes — just routes, resources, and the request object in your hands.

---

## Table of Contents

- [Installation](#installation)
- [Key Features](#key-features)
- [Quickstart](#quickstart)
- [Dynamic Routes](#dynamic-routes)
- [Request Body Validation with BaseModel](#request-body-validation-with-basemodel)
- [API Key Authentication](#api-key-authentication)
- [Generating Unit Tests](#generating-unit-tests)
- [Auto-generated Docs](#auto-generated-docs)

---

## Installation

PebaREST is not yet published on PyPI. Install it directly from GitHub:

```bash
pip install git+https://github.com/EderMiqueias/PebaREST.git
```

No external dependencies are required — the framework runs on Python's standard library.

---

## Key Features

- **Resource-based routing** — map URL paths to classes with HTTP method handlers (`get`, `post`, `put`, `patch`, `delete`, …).
- **Dynamic routes** — declare path parameters with `{param}` syntax; access them via `request.path_params`.
- **Typed body validation** — use `BaseModel` to automatically parse and validate the JSON request body.
- **Built-in authentication** — plug in `APIKeyAuthenticator` or implement your own `BaseAuthenticator`.
- **Zero magic** — the WSGI callable is explicit, testable, and fully transparent.
- **Test generation** — generate `unittest` files from a simple test-case dictionary via `app.generate_tests()`.
- **OpenAPI docs** — enable a `/docs` endpoint with a single constructor flag.

---

## Quickstart

The minimal example: one route, one resource, one server.

```python
from wsgiref.simple_server import make_server

from pebarest import App
from pebarest.models import Resource, Request


class HelloResource(Resource):
    def get(self, request: Request):
        return {"message": "Hello, World!"}


app = App(__name__, default_headers={"Content-Type": "application/json"})
app.add_route("/", HelloResource())

with make_server("", 8000, app) as httpd:
    print("Server listening on http://127.0.0.1:8000")
    httpd.serve_forever()
```

```bash
$ curl http://127.0.0.1:8000/
{"message": "Hello, World!"}
```

---

## Dynamic Routes

Declare a path parameter by wrapping its name in curly braces. PebaREST automatically populates `request.path_params` with the matched values.

```python
from wsgiref.simple_server import make_server

from pebarest import App
from pebarest.models import Resource, Request


USERS = {
    "1": {"id": "1", "name": "Alice"},
    "2": {"id": "2", "name": "Bob"},
}


class UserDetailResource(Resource):
    def get(self, request: Request):
        user_id = request.path_params.get("user_id")
        user = USERS.get(user_id)
        if user is None:
            return {"error": f"User '{user_id}' not found."}, 404
        return user

    def delete(self, request: Request):
        user_id = request.path_params.get("user_id")
        user = USERS.pop(user_id, None)
        if user is None:
            return {"error": f"User '{user_id}' not found."}, 404
        return {"deleted": user}


app = App(__name__, default_headers={"Content-Type": "application/json"})
app.add_route("/users/{user_id}", UserDetailResource())

with make_server("", 8000, app) as httpd:
    print("Server listening on http://127.0.0.1:8000")
    httpd.serve_forever()
```

```bash
$ curl http://127.0.0.1:8000/users/1
{"id": "1", "name": "Alice"}

$ curl http://127.0.0.1:8000/users/99
{"error": "User '99' not found."}
```

Multiple dynamic segments are supported in the same path:

```python
app.add_route("/posts/{post_id}/comments/{comment_id}", CommentDetailResource())
```

Both `post_id` and `comment_id` will be available in `request.path_params`.

---

## Request Body Validation with BaseModel

Annotate the `request` parameter with `Request[YourModel]` to have the JSON body automatically parsed and validated against a typed model.

```python
from wsgiref.simple_server import make_server

from pebarest import App, BaseModel
from pebarest.models import Resource, Request


class Item(BaseModel):
    name: str
    quantity: int


class ItemResource(Resource):
    def post(self, request: Request[Item]):
        item: Item = request.body  # already validated and typed
        return {"received": item.name, "qty": item.quantity}, 201


app = App(__name__, default_headers={"Content-Type": "application/json"})
app.add_route("/items", ItemResource())

with make_server("", 8000, app) as httpd:
    print("Server listening on http://127.0.0.1:8000")
    httpd.serve_forever()
```

If a required field is missing or has the wrong type, PebaREST returns a `422 Unprocessable Entity` response automatically.

---

## API Key Authentication

Pass an `APIKeyAuthenticator` instance when creating the `App`. Every request will be validated before reaching the resource handler, and the resolved client info is available on `request.client_info`.

```python
from pebarest import App
from pebarest.auth import APIKeyAuthenticator
from pebarest.models import Resource, Request

auth = APIKeyAuthenticator(
    valid_keys={"supersecret-key-123": "client-A"},
    header_name="X-API-Key",
)


class ProtectedResource(Resource):
    def get(self, request: Request):
        return {"client": request.client_info["client_id"]}


app = App(__name__, auth_handler=auth)
app.add_route("/protected", ProtectedResource())
```

---

## Generating Unit Tests

PebaREST can scaffold a `unittest` file for your API from a declarative test-case dictionary:

```python
app.generate_tests(
    {
        "/items": {
            "POST": {"name": "Apple", "quantity": 10}
        }
    },
    output_file="tests/test_items_api.py",
)
```

Run the script once (e.g., `python app.py`) and the test file is created. Requires `is_debug=True` (the default).

---

## Auto-generated Docs

Enable the built-in OpenAPI 3.1.0 documentation endpoint with a single flag:

```python
app = App(__name__, generate_docs=True)
```

The schema is then available at `GET /docs`.

---

## License

See [LICENSE](LICENSE) for details.
PebaRest Framework, fast to code, take the control of your application.
