from framework.contracts.service_provider import ServiceProvider


class AppProvider(ServiceProvider):
    def register(self, app):
        app.state["name"] = "MyFramework"

    def boot(self, app):
        app.state["ready"] = True
