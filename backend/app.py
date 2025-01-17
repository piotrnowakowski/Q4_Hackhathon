from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
import os
from pinecone import Pinecone, ServerlessSpec

# Load environment variables or replace with your keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "your_pinecone_api_key_here")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "your_pinecone_environment_here")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX", "your_pinecone_index_name_here")

# Initialize OpenAI
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=OPENAI_API_KEY)

# Initialize Pinecone client
pinecone_client = Pinecone(api_key=PINECONE_API_KEY)

# Check if the index exists and create it if necessary
if PINECONE_INDEX_NAME not in [index.name for index in pinecone_client.list_indexes()]:
    pinecone_client.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region=PINECONE_ENVIRONMENT
        )
    )

# Connect to the Pinecone index
index = pinecone_client.Index(PINECONE_INDEX_NAME)

# Initialize LangChain vector store
vectorstore = PineconeVectorStore(index=index, embedding=embeddings, text_key="text")

# FastAPI app
def create_app():
    app = FastAPI()

    # Add CORS middleware to allow communication with frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
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
        try:
            vectorstore.add_texts(
                texts=[data.text],
                metadatas=[data.metadata],
                ids=[data.id]
            )
            return {"message": "Document upserted successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error upserting document: {str(e)}")

    @app.post("/query")
    async def query_pinecone(data: QueryRequest):
        try:
            results = vectorstore.similarity_search(query=data.text, k=3)
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
            raise HTTPException(status_code=500, detail=f"Error querying Pinecone: {str(e)}")

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "message": "API is running smoothly"}

    return app

# Create the FastAPI app
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="debug")