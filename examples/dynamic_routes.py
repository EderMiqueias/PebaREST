from wsgiref.simple_server import make_server

from pebarest import App
from pebarest.models import Resource, Request


# Simulated in-memory database
USERS = {
    "1": {"id": "1", "name": "Alice", "role": "admin"},
    "2": {"id": "2", "name": "Bob",   "role": "user"},
}

POSTS = {
    "1": {
        "title": "Hello PebaREST",
        "comments": {
            "1": {"id": "1", "text": "Great framework!"},
            "2": {"id": "2", "text": "Love it."},
        },
    }
}


# --- /users  (static) -------------------------------------------------------

class UsersResource(Resource):
    def get(self, request: Request, *args, **kwargs):
        return list(USERS.values())


# --- /users/{user_id}  (dynamic) --------------------------------------------

class UserDetailResource(Resource):
    def get(self, request: Request,):
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


# --- /posts/{post_id}/comments/{comment_id}  (two dynamic segments) ---------

class CommentDetailResource(Resource):
    def get(self, request: Request):
        post_id = request.path_params.get("post_id")
        comment_id = request.path_params.get("comment_id")
        post = POSTS.get(post_id)
        if post is None:
            return {"error": f"Post '{post_id}' not found."}, 404
        comment = post["comments"].get(comment_id)
        if comment is None:
            return {"error": f"Comment '{comment_id}' not found."}, 404
        return comment


# --- App setup --------------------------------------------------------------

app = App(__name__, default_headers={'Content-Type': 'application/json'})

# Static route
app.add_route('/users', UsersResource())

# Dynamic route — single path parameter
app.add_route('/users/{user_id}', UserDetailResource())

# Dynamic route — two path parameters
app.add_route('/posts/{post_id}/comments/{comment_id}', CommentDetailResource())


# --- Start server -----------------------------------------------------------

with make_server('', 8000, app) as httpd:
    print("Server listening on http://127.0.0.1:8000")
    print()
    print("Try:")
    print("  GET  http://127.0.0.1:8000/users")
    print("  GET  http://127.0.0.1:8000/users/1")
    print("  GET  http://127.0.0.1:8000/users/99       <- 404")
    print("  GET  http://127.0.0.1:8000/posts/1/comments/2")
    httpd.serve_forever()
