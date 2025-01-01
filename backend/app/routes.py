from flask import Blueprint, jsonify, request
from .realtime_api import get_ephemeral_key
from flask import Blueprint, jsonify, request
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings
import pinecone
import os

# Initialize Pinecone
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))
index = pinecone.Index(os.getenv("PINECONE_INDEX"))  # Replace with your Pinecone index name
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
main = Blueprint("main", __name__)

@main.route("/query-pinecone", methods=["POST"])
def query_pinecone():
    """
    New endpoint to query Pinecone with OpenAI embeddings.
    """
    try:
        data = request.json
        query = data.get("query")
        if not query:
            return jsonify({"error": "Query is required"}), 400

        # Generate embeddings using OpenAI
        embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        vector_store = Pinecone(index_name=index, embedding=embeddings)
        retriever = vector_store.as_retriever(search_type="similarity")

        # Retrieve documents from Pinecone
        documents = retriever.retrieve(query)
        results = [doc.page_content for doc in documents]

        return jsonify({"success": True, "results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
