import pinecone
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings

# Initialize Pinecone
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))

def retrieve_from_pinecone(query):
    embeddings = OpenAIEmbeddings()
    index = Pinecone(index_name="your-pinecone-index", embedding=embeddings)
    retriever = index.as_retriever(search_type="similarity")

    # Query the retriever
    documents = retriever.retrieve(query)
    return {"results": [doc.page_content for doc in documents]}
