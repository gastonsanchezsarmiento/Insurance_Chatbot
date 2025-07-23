# indexador.py

import os
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from dotenv import load_dotenv
load_dotenv()


openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
else:
    raise ValueError("No se encontró la variable OPENAI_API_KEY en el archivo .env")

def construir_y_guardar_vector_index():
    print("📥 Leyendo PDFs desde 'data/'...")
    archivos = [f for f in os.listdir("data") if f.endswith(".pdf")]
    if not archivos:
        print("❌ No hay archivos PDF en la carpeta 'data'.")
        return

    loaders = [PyPDFLoader(f"data/{f}") for f in archivos]
    documentos = []
    for loader in loaders:
        documentos.extend(loader.load())

    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(documentos)

    print("🔄 Generando embeddings y creando índice FAISS...")
    vectordb = FAISS.from_documents(chunks, OpenAIEmbeddings())
    vectordb.save_local("vector_index/")
    print("✅ Índice guardado en 'vector_index/'.")

if __name__ == "__main__":
    construir_y_guardar_vector_index()
