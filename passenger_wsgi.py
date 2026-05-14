import os
import sys

# Add the current directory to sys.path so app can be found
sys.path.insert(0, os.path.dirname(__file__))

from a2wsgi import ASGIMiddleware
from public.index import app

application = ASGIMiddleware(app)
