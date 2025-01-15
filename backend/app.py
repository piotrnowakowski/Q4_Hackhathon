from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import pinecone
import os

# Load environment variables or replace with your keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "your_pinecone_api_key")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "your_pinecone_environment")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "your_index_name")

# Initialize OpenAI and Pinecone
openai.api_key = OPENAI_API_KEY
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

# Connect to Pinecone index
index = pinecone.Index(PINECONE_INDEX)

def create_app():
    app = FastAPI()

    # Add CORS middleware to allow communication with frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Replace "*" with frontend's URL in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Pydantic model for input validation
    class QueryRequest(BaseModel):
        text: str

    @app.post("/query")
    async def query_pinecone(data: QueryRequest):
        """
        Accepts a piece of text, generates its embedding using OpenAI,
        and queries Pinecone to find the closest matches.
        """
        # Embed the input text using OpenAI
        try:
            response = openai.Embedding.create(
                input=data.text,
                model="text-embedding-ada-002"
            )
            embedding = response["data"][0]["embedding"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating embedding: {e}")

        # Query the Pinecone index
        try:
            results = index.query(vector=embedding, top_k=3, include_metadata=True)
            return {"matches": results["matches"]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error querying Pinecone: {e}")

    @app.get("/")
    async def root():
        """Root endpoint to check if the API is running."""
        return {"message": "FastAPI and Pinecone are ready!"}

    @app.get("/health")
    async def health_check():
        """Health check endpoint to ensure the API is running smoothly."""
        return {"status": "ok", "message": "API is running smoothly"}

    return app

# Create the application
app = create_app()

if __name__ == "__main__":
    # Run the FastAPI app using Uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="debug")
