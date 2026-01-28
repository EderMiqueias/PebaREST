from typing import Dict, Any


class TestGenerator:
    routes: Dict[str, Any]

    def __init__(self, app):
        self.app = app
        self.routes = app.routes_manager.routes

    def generate(self, test_cases: Dict[str, Dict[str, Any]] = None, output_file="tests/test_api_generated.py"):
        pass
