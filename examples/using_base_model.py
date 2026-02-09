from wsgiref.simple_server import make_server

from pebarest import BaseModel, App
from pebarest.models import Resource, Request


class Item(BaseModel):
    name: str
    quantity: int


# Class for simple resource
class GreetingResource(Resource):
    def post(self, request: Request[Item], *args, **kwargs):
        print(request.body)
        print(request.params)
        return {"message": "Hello my little peba!"}


app = App(__name__, default_headers={'Content-Type': 'application/json'}, generate_docs=True)

# Add a new route path
app.add_route('/greeting', GreetingResource())

# Start the server
with make_server('', 8000, app) as httpd:
    print("Server listening on http://127.0.0.1:8000")
    httpd.serve_forever()
