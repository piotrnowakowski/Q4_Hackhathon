import os
from pathlib import Path
import time
import uuid
import numpy as np
from pinecone import Pinecone
import cohere
from dotenv import load_dotenv

# Get the parent directory (backend) and load .env from there
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "")
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
EMBED_MODEL = os.getenv("EMBED_MODEL", "embed-multilingual-v3.0")

# Initialize Pinecone connection
pc = Pinecone(api_key=PINECONE_API_KEY)

# Retrieve the existing index
index = pc.Index(PINECONE_INDEX_NAME)

# Initialize Cohere client
co = cohere.Client(api_key=COHERE_API_KEY)

def load_data_to_pinecone(texts):
    """
    Embeds a list of texts using Cohere's 'embed-multilingual-v3.0' model,
    then upserts the vectors into an existing Pinecone index.

    Args:
        texts (List[str]): The list of documents or sentences to be embedded and upserted.
    """

    print(f"Started embedding {len(texts)} texts using '{EMBED_MODEL}'...")
    start_time = time.time()
    
    # Get embeddings from Cohere
    response = co.embed(
        texts=texts,
        model=EMBED_MODEL,
        input_type="search_document"
    )
    
    # Extract the embeddings from the response
    embeddings = response.embeddings  # This is the key change
    
    print(f"Total embedding time: {time.time() - start_time:.2f} seconds")
    
    to_upsert = []
    for i, text in enumerate(texts):
        record_id = f"id{i}"
        metadata = {"text": text}
        to_upsert.append((record_id, embeddings[i], metadata))
    
    # Upsert to Pinecone
    index.upsert(vectors=to_upsert)

def query_pinecone(query, top_k=5):
    """
    Embeds a single query using Cohere's 'embed-multilingual-v3.0' model
    and searches the existing Pinecone index for the top_k most similar results.

    Args:
        query (str): The user query.
        top_k (int): Number of top matches to retrieve.

    Returns:
        list: Pinecone 'matches' containing metadata and similarity scores.
    """
    print(f"\nRunning semantic search for query: '{query}'")
    start_time = time.time()

    # Create the query embedding
    query_embedding = co.embed(
        texts=[query],
        model=EMBED_MODEL,
        input_type='search_query'
    ).embeddings[0]

    # Query Pinecone
    response = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    end_time = time.time()

    matches = response['matches']
    print(f"Query time: {end_time - start_time:.2f} seconds")
    print("Top matches:")
    for match in matches:
        score = match['score']
        text_data = match['metadata']['text']
        print(f"{score:.2f}: {text_data}")
    return matches
