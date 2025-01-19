from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import os
import time

# Load environment variables or replace with your keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key")

# Initialize OpenAI Embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=OPENAI_API_KEY)

# Initialize ChromaDB vector store
vectorstore = Chroma(
    collection_name="my_chroma_collection",
    persist_directory="chroma_db",  # Directory to persist ChromaDB data
    embedding_function=embeddings
)

# FastAPI app
def create_app():
    app = FastAPI()

    # Add CORS middleware to allow communication with frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Replace with specific origins in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Define Pydantic models
    class QueryRequest(BaseModel):
        text: str

    class UpsertRequest(BaseModel):
        id: str
        text: str
        metadata: dict

    # Define API endpoints
    @app.post("/upsert")
    async def upsert_document(data: UpsertRequest):
        """
        Upserts a document into the ChromaDB collection.
        """
        try:
            # Add the document to ChromaDB
            vectorstore.add_texts(
                texts=[data.text],
                metadatas=[data.metadata],
                ids=[data.id]
            )
            return {"message": "Document upserted successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error upserting document: {str(e)}")

    @app.post("/query")
    async def query_chroma(data: QueryRequest):
        """
        Queries the ChromaDB collection for similar documents.
        """
        try:
            # Step 1: Generate Embedding
            start_embedding = time.time()
            query_embedding = embeddings.embed_query(data.text)
            end_embedding = time.time()

            # Step 2: Perform Similarity Search
            start_query = time.time()
            results = vectorstore.similarity_search_by_vector(query_embedding, k=3)
            end_query = time.time()

            # Return timing information for debugging
            return {
                "matches": [
                    {
                        "id": result.metadata.get("id"),
                        "text": result.page_content,
                        "metadata": result.metadata,
                    }
                    for result in results
                ],
                "timing": {
                    "embedding_time": end_embedding - start_embedding,
                    "query_time": end_query - start_query,
                    "total_time": (end_embedding - start_embedding) + (end_query - start_query)
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error querying ChromaDB: {str(e)}")

    @app.get("/health")
    async def health_check():
        """
        Health check endpoint.
        """
        return {"status": "ok", "message": "API is running smoothly"}

    return app


# Create the FastAPI app
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="debug")