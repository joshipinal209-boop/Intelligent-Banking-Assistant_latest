import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

# Load environment variables
load_dotenv()

def get_vectorstore():
    """
    Initializes and returns the Chroma vector store instance.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        task_type="retrieval_document",
        google_api_key=api_key
    )
    
    persist_directory = os.getenv("VECTOR_DB_PATH", "./data/vector/chroma")
    
    return Chroma(
        collection_name="bank_docs",
        embedding_function=embeddings,
        persist_directory=persist_directory
    )

def ingest_documents(directory_path="data/seed/vector_docs/"):
    """
    Ingests markdown documents from the specified directory into ChromaDB.
    Ensures idempotency by checking if documents already exist.
    """
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist. Skipping ingestion.")
        return
        
    loader = DirectoryLoader(directory_path, glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()
    
    if not documents:
        print("No documents found to ingest.")
        return

    text_splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=80)
    docs = text_splitter.split_documents(documents)
    
    vectorstore = get_vectorstore()
    
    # Idempotency check: If collection has items, skip ingestion
    # For a seed script, this is usually sufficient. 
    # If the user wants to force reload, they would delete the persist_directory.
    count = vectorstore._collection.count()
    if count > 0:
        print(f"Collection 'bank_docs' already contains {count} items. Skipping ingestion to ensure idempotency.")
        return vectorstore
        
    print(f"Ingesting {len(docs)} document chunks into 'bank_docs'...")
    vectorstore.add_documents(docs)
    vectorstore.persist()
    print("Ingestion complete.")
    return vectorstore

def get_retriever():
    """
    Returns a retriever for the bank_docs collection.
    """
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever(search_kwargs={"k": 3})

if __name__ == "__main__":
    ingest_documents()
