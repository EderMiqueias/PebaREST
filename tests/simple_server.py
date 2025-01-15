from pebarest import App
from pebarest.models import Resource

from wsgiref.simple_server import make_server


# Class for simple resource
class GreetingResource(Resource):
    def get(self, request, *args, **kwargs):
        return {"message": "Hello my little peba!"}


app = App(default_headers={'Content-Type': 'application/json'})

# Add a new route path
app.add_route('/greeting', GreetingResource())

# Start the server
with make_server('', 8000, app) as httpd:
    print("Server listening on http://127.0.0.1:8000")
    httpd.serve_forever()
