"""REST endpoints for the in-memory counter service."""

from flask import abort, jsonify, url_for
from service import app

COUNTERS = {}


@app.route("/health", methods=["GET"])
def health():
    """Return service health."""
    return jsonify(status="OK"), 200


@app.route("/", methods=["GET"])
def index():
    """Return service metadata."""
    return jsonify(
        status=200,
        message="Hit Counter Service",
        version="1.0.0",
        url=url_for("list_counters", _external=True),
    ), 200


@app.route("/counters", methods=["GET"])
def list_counters():
    """List all counters."""
    return jsonify([
        {"name": name, "counter": value}
        for name, value in sorted(COUNTERS.items())
    ]), 200


@app.route("/counters/<name>", methods=["POST"])
def create_counter(name):
    """Create a counter, initially zero."""
    if name in COUNTERS:
        abort(409, description="Counter already exists")
    COUNTERS[name] = 0
    return (
        jsonify(name=name, counter=0),
        201,
        {"Location": url_for("read_counter", name=name, _external=True)},
    )


@app.route("/counters/<name>", methods=["GET"])
def read_counter(name):
    """Read a counter."""
    if name not in COUNTERS:
        abort(404, description="Counter not found")
    return jsonify(name=name, counter=COUNTERS[name]), 200


@app.route("/counters/<name>", methods=["PUT"])
def update_counter(name):
    """Increment an existing counter."""
    if name not in COUNTERS:
        abort(404, description="Counter not found")
    COUNTERS[name] += 1
    return jsonify(name=name, counter=COUNTERS[name]), 200


@app.route("/counters/<name>", methods=["DELETE"])
def delete_counter(name):
    """Delete a counter. Deleting a nonexistent counter is idempotent."""
    COUNTERS.pop(name, None)
    return "", 204


def reset_counters():
    """Clear test data only while Flask is in testing mode."""
    if not app.testing:
        raise RuntimeError("reset_counters requires testing mode")
    COUNTERS.clear()
