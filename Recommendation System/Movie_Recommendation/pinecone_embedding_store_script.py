from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone.grpc import PineconeGRPC as Pinecone
from langchain.docstore.document import Document
from pinecone import ServerlessSpec
from dotenv import load_dotenv
import pandas as pd
import os

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "movie-recommendation"

# Create the index if it doesn't exist
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384, 
        metric="cosine", 
        spec=ServerlessSpec(
            cloud="aws", 
            region="us-east-1"
        ) 
    ) 

movie_df = pd.read_csv("movie_data_preprocessed.csv")
embedding_fn = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Convert to LangChain documents
docs = [
    Document(page_content=row["tags"], metadata={"title": row["title"]})
    for _, row in movie_df.iterrows()
]

docsearch = PineconeVectorStore.from_documents(
    documents=docs,
    embedding=embedding_fn,
    index_name=index_name  # string, not an Index object
)
