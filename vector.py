from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

df = pd.read_csv("crop_disease_data.csv")
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

db_location = "./chroma_agriculture_db"
add_documents = not os.path.exists(db_location)

if add_documents:
    documents = []
    ids = []
    
    for i, row in df.iterrows():
        document = Document(
            page_content=row["Disease"] + " " + row["Symptoms"] + " " + row["Treatment"],
            metadata={"crop_type": row["CropType"], "severity": row["Severity"], "date_observed": row["DateObserved"]},
            id=str(i)
        )
        ids.append(str(i))
        documents.append(document)
        
vector_store = Chroma(
    collection_name="agriculture_disease_detection",
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_documents:
    vector_store.add_documents(documents=documents, ids=ids)
    
retriever = vector_store.as_retriever(
    search_kwargs={"k": 5}
)
