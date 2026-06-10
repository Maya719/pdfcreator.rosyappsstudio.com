# /framework/http/middleware_pipeline.py


class MiddlewarePipeline:
    def __init__(self, app):
        self.app = app

    def load(self):
        from app.middleware import all_middlewares

        for middleware in all_middlewares:
            self.app.add_middleware(middleware)
