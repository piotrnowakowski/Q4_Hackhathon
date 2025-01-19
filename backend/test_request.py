import requests
import time

# Base URL of the FastAPI application
BASE_URL = "http://localhost:5000"

# Documents to upload
documents = [
    {
        "id": "doc1",
        "text": "Quantum computing has the potential to revolutionize cryptography and material science.",
        "metadata": {
            "category": "technology",
            "language": "English"
        }
    },
    {
        "id": "doc2",
        "text": "The discovery of gravitational waves confirms Einstein's theory of general relativity.",
        "metadata": {
            "category": "science",
            "language": "English"
        }
    },
    {
        "id": "doc3",
        "text": "Shakespeare's Hamlet is considered one of the greatest works of literature.",
        "metadata": {
            "category": "literature",
            "language": "English"
        }
    },
    {
        "id": "doc4",
        "text": "Lionel Messi's performance in the FIFA World Cup was widely celebrated.",
        "metadata": {
            "category": "sports",
            "language": "English"
        }
    },
    {
        "id": "doc5",
        "text": "The Renaissance was a cultural movement that profoundly affected European intellectual life.",
        "metadata": {
            "category": "history",
            "language": "English"
        }
    }
]

# Upload documents to ChromaDB
def load_documents():
    url = f"{BASE_URL}/upsert"
    for doc in documents:
        response = requests.post(url, json=doc)
        if response.status_code == 200:
            print(f"Document {doc['id']} uploaded successfully!")
        else:
            print(f"Failed to upload document {doc['id']}: {response.status_code}, {response.json()}")

# Test the /query endpoint
def test_query():
    start_querry = time.time()
    url = f"{BASE_URL}/query"
    payload = {
        "text": "integration with cryptography",
        "top_k": 3  # Number of results to retrieve
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Query Response:")
        print(response.json())
    else:
        print(f"Failed to query: {response.status_code}, {response.json()}")
    end_query = time.time()
    print(f"Query time: {end_query - start_querry} seconds")

if __name__ == "__main__":
    print("Uploading documents to ChromaDB...")
    load_documents()
    print("Documents uploaded successfully!")
    
    print("\nTesting /query endpoint...")
    test_query()
