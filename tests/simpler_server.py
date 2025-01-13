from pebarest import App

from wsgiref.simple_server import make_server


# Class for simple resource
class GreetingResource:

    def get(self, request):
        return {"message": "Hello my little peba!"}


app = App()

# Add a neu route path
app.add_route('/greeting', GreetingResource())

# start the server
with make_server('', 8000, app) as httpd:
    print("Server listening on http://127.0.0.1:8000")
    httpd.serve_forever()
