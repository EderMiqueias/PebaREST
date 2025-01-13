class RouteAlreadyExistsError(Exception):
    route_path: str

    def __init__(self, route_path: str):
        self.route_path = route_path
