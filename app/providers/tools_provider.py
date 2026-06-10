from framework.contracts.service_provider import ServiceProvider
from config.tools import TOOLS


class ToolsProvider(ServiceProvider):
    def register(self, app):
        app.state["tools"] = TOOLS
        app.templates.env.globals["tools"] = app.state["tools"]

    def boot(self, app):
        app.state["tools_ready"] = True
