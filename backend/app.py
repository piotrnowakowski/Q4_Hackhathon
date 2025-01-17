from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import os

# Load environment variables or replace with your keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")

# Initialize OpenAI Embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-large", openai_api_key=OPENAI_API_KEY)


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
            # Perform similarity search using the query text
            results = vectorstore.similarity_search(data.text, k=3)
            return {
                "matches": [
                    {
                        "id": result.metadata.get("id"),
                        "text": result.page_content,
                        "metadata": result.metadata,
                    }
                    for result in results
                ]
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