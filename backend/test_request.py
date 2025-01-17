import requests

# Set the base URL for the FastAPI application
BASE_URL = "http://localhost:5000"

# Test the `/upsert` endpoint
'''def test_upsert():
    url = f"{BASE_URL}/upsert"
    payload = {
        "id": "document1",
        "text": "This is a sample document about FastAPI and Pinecone integration.",
        "metadata": {"category": "integration", "language": "English"}
    }
    response = requests.post(url, json=payload)
    print("Upsert Response:", response.status_code, response.json())'''

# Test the `/query` endpoint
def test_query():
    url = f"{BASE_URL}/query"
    payload = {
        "text": "integration with FastAPI"
    }
    response = requests.post(url, json=payload)
    print("Query Response:", response.status_code, response.json())

# Test the `/health` endpoint
def test_health():
    url = f"{BASE_URL}/health"
    response = requests.get(url)
    print("Health Check Response:", response.status_code, response.json())

if __name__ == "__main__":
    print("Testing /health endpoint...")
    test_health()
    print("\nTesting /upsert endpoint...")
    #test_upsert()
    print("\nTesting /query endpoint...")
    test_query()
