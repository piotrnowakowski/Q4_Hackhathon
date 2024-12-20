from flask import Blueprint, jsonify, request
from .realtime_api import get_ephemeral_key

main = Blueprint("main", __name__)

@main.route("/session", methods=["GET"])
def session():
    """
    Endpoint for frontend to request an ephemeral API key for WebRTC connection.
    """
    try:
        ephemeral_key = get_ephemeral_key()
        return jsonify(ephemeral_key)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
