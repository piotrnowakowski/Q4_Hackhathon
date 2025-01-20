from flask import Blueprint, jsonify, request
from .realtime_api import get_ephemeral_key
from .query_pinecone import query_pinecone  # Import the query_pinecone function

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

@main.route("/search", methods=["POST"])
def search():
    """
    Endpoint to perform semantic search using Pinecone.
    """
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Query is required"}), 400
        
        query = data['query']
        top_k = data.get('top_k', 5)  # Optional parameter with default value
        
        matches = query_pinecone(query, top_k)
        
        # Format the response
        results = [{
            "score": match['score'],
            "text": match['metadata']['text']
        } for match in matches]
        
        return jsonify({
            "results": results,
            "query": query,
            "count": len(results)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
