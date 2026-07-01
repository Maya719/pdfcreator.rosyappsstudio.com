import os
import sys

# Add the current directory to sys.path so app can be found
sys.path.insert(0, os.path.dirname(__file__))

from a2wsgi import ASGIMiddleware
from bootstrap.autoload import bootstrap

app = bootstrap()
application = ASGIMiddleware(app)
