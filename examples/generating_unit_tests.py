from pebarest import BaseModel, App
from pebarest.models import Resource, Request


class Item(BaseModel):
    name: str
    quantity: int


# Class for simple resource
class GreetingResource(Resource):
    def get(self, request: Request[Item], *args, **kwargs):
        print(request.body)
        print(request.params)
        return {"message": "Hello my little peba!"}


app = App(__name__, default_headers={'Content-Type': 'application/json'})

# Add a new route path
app.add_route('/greeting', GreetingResource())

if __name__ == '__main__':
    app.generate_tests(
        {
            '/greeting': {
                'POST': {
                    "name": "Apple",
                    "quantity": 10
                }
            }
        }, output_file="tests/test_greeting_api.py"
    )
