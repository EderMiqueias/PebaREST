class RouteAlreadyExistsError(Exception):
    route_path: str

    def __init__(self, route_path: str):
        self.route_path = route_path


class MethodNotAllowedError(Exception):
    method: str

    def __init__(self, method: str):
        self.method = method
        self.title = f'405 Method Not Allowed'
