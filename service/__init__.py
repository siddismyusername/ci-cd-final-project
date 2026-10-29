"""Flask application for the CI/CD counter-service assignment."""

import logging
from flask import Flask

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Register routes after the app is constructed.
from service import routes  # noqa: E402,F401

app.logger.info("Initializing counter-service")
app.logger.info("SERVICERUNNING")
app.logger.info("Listening on port 8000")
