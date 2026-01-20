from typing import Optional
from pebarest import App, BaseModel
from pebarest.models import Resource, Request

from wsgiref.simple_server import make_server
from time import sleep
import os
import uvicorn


class Item(BaseModel):
    name: str
    quantity: int
    description: Optional[str] = None


# Class for simple resource
class GreetingResource(Resource):
    def get(self, request: Request[Item], *args, **kwargs):
        print(request.body)
        return {"message": "Hello my little peba!"}


app = App(__name__, default_headers={'Content-Type': 'application/json'})

# Add a new route path
app.add_route('/greeting', GreetingResource())

# Start the server
with make_server('', 8000, app) as httpd:
    print("Server listening on http://127.0.0.1:8000")
    httpd.serve_forever()

# if __name__ == "__main__":
#     uvicorn.run("simple_server_asgi:app", host="0.0.0.0", port=8080, reload=True)
