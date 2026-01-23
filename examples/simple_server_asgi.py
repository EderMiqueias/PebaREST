from pebarest import App, BaseModel
from pebarest.models import Resource, Request

from time import sleep
import uvicorn


class Item(BaseModel):
    name: str
    quantity: int

# Class for simple resource
class GreetingResource(Resource):
    def get(self, request: Request[Item], *args, **kwargs):
        sleep(3)
        print(request.body)
        return {"message": "Hello my little peba!"}


app = App(__name__, default_headers={'Content-Type': 'application/json'})

# Add a new route path
app.add_route('/greeting', GreetingResource())

if __name__ == "__main__":
    uvicorn.run("simple_server_asgi:app", host="0.0.0.0", port=8080, reload=True)
