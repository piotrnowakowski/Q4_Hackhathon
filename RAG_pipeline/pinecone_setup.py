import pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeEmbeddings
import os
from dotenv import load_dotenv

def load_markdown_file(markdown_path):
    """
    Loads text from a Markdown file.

    Args:
        markdown_path (str): Path to the Markdown file.

    Returns:
        str: Text content of the Markdown file.
    """
    with open(markdown_path, 'r', encoding='utf-8') as file:
        return file.read()

def initialize_pinecone(api_key, environment):
    """
    Initializes Pinecone with API key and environment.

    Args:
        api_key (str): Pinecone API key.
        environment (str): Pinecone environment (e.g., 'us-west1-gcp').
    """
    pinecone.init(api_key=api_key, environment=environment)

def create_or_connect_index(index_name, dimension):
    """
    Creates or connects to a Pinecone index.

    Args:
        index_name (str): Name of the Pinecone index.
        dimension (int): Dimension of the embeddings.

    Returns:
        pinecone.Index: Pinecone index instance.
    """
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(index_name, dimension=dimension)
    return pinecone.Index(index_name)

def process_markdown_to_pinecone(markdown_path, index_name, api_key, environment, model_name="multilingual-e5-large"):
    """
    Processes a Markdown file, generates embeddings, and loads them into Pinecone.

    Args:
        markdown_path (str): Path to the Markdown file.
        index_name (str): Name of the Pinecone index.
        api_key (str): Pinecone API key.
        environment (str): Pinecone environment.
        model_name (str): Name of the embedding model to use.
    """
    # Initialize Pinecone
    initialize_pinecone(api_key, environment)

    # Load Markdown file
    text_content = load_markdown_file(markdown_path)

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_text(text_content)

    # Generate embeddings
    embeddings = PineconeEmbeddings(model=model_name)
    embedded_texts = embeddings.embed_documents(texts)

    # Create or connect to the Pinecone index
    index = create_or_connect_index(index_name, dimension=len(embedded_texts[0]))

    # Prepare metadata and upload data
    metadatas = [{"filename": markdown_path} for _ in texts]
    vectors = [
        {"id": f"vec_{i}", "values": embedded_texts[i], "metadata": metadatas[i]}
        for i in range(len(embedded_texts))
    ]
    index.upsert(vectors)

    print(f"Data from {markdown_path} loaded into Pinecone index {index_name}.")

# Example usage
if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    markdown_path = os.getenv("MARKDOWN_PATH", "output_file.md")  # Default to "output_file.md" if not set
    index_name = os.getenv("INDEX_NAME", "your_index_name")  # Default to "your_index_name" if not set
    api_key = os.getenv("PINECONE_API_KEY", "your_pinecone_api_key")  # Default to "your_pinecone_api_key" if not set
    environment = os.getenv("PINECONE_ENVIRONMENT", "your_pinecone_environment")  # Default to "your_pinecone_environment" if not set
    process_markdown_to_pinecone(markdown_path, index_name, api_key, environment)
