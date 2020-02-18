import logging.config
import os

import yaml
from flask import Flask
from server.routes import inwx_router

# Load logging config
if os.path.isfile("logging_config.yaml"):
    with open("logging_config.yaml", "r") as f:
        logging.config.dictConfig(yaml.load(f, Loader=yaml.FullLoader))
else:
    print("[!] Could not find logging config")

LOGGER = logging.getLogger(__name__)

app = Flask(__name__)

app.register_blueprint(inwx_router)
