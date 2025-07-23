# agente.py

from cmd import PROMPT
from dotenv import load_dotenv
load_dotenv()

import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.prompts import PromptTemplate 

# Configura tus claves
openai_api_key = os.getenv("OPENAI_API_KEY")
serpapi_api_key = os.getenv("SERPAPI_API_KEY")

if not openai_api_key:
    raise ValueError("No se encontró la variable OPENAI_API_KEY en el archivo .env")
if not serpapi_api_key:
    raise ValueError("No se encontró la variable SERPAPI_API_KEY en el archivo .env")

os.environ["OPENAI_API_KEY"] = openai_api_key
os.environ["SERPAPI_API_KEY"] = serpapi_api_key

# Cargar índice desde disco
def cargar_vectordb_desde_disco():
    index_path = "vector_index/"
    if not os.path.exists(index_path):
        raise FileNotFoundError("No se encontró el índice. Ejecuta primero indexador.py.")
    return FAISS.load_local(index_path, OpenAIEmbeddings(), allow_dangerous_deserialization=True)

# Herramienta local inteligente
def crear_tool_busqueda_local(vectordb):
    def consulta_local(query: str) -> str:
        docs = vectordb.similarity_search(query, k=3)
        if not docs:
            return "❌ No encontré información relevante en los PDFs."

        contenido = "\n\n".join([doc.page_content for doc in docs])
        if len(contenido.strip()) < 100:
            return "❌ No encontré información clara en los documentos."

        return f"✅ Esto fue lo que encontré en los PDFs:\n\n{contenido}"
    
    return Tool(
        name="ConsultaPDF",
        func=consulta_local,
        description="Busca respuestas en PDFs locales cargados previamente si el tema esta relacionado a pólizas."
    )

# Herramienta de búsqueda web
def crear_tool_web():
    return Tool(
        name="BusquedaEnLinea",
        func=DuckDuckGoSearchRun().run,
        description="Usa búsqueda web si no encuentras la respuesta en PDFs."
    )


# Crear agente
def crear_agente(tools):
    llm = ChatOpenAI(temperature=0, model_name="gpt-4")  # O usa gpt-3.5-turbo

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    prompt_template = PromptTemplate.from_template( 
        
    )
    
    agente = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        memory=memory, 
        
    )
    return agente

# Main
def main():
    print("📦 Cargando índice vectorial...")
    vectordb = cargar_vectordb_desde_disco()

    herramienta_pdf = crear_tool_busqueda_local(vectordb)
    herramienta_web = crear_tool_web()

    agente = crear_agente([herramienta_pdf, herramienta_web])

    print("\n🤖 Agente listo. Escribe tu pregunta o 'salir' para terminar.")
    while True:
        pregunta = input("\n🧑 Tú: ")
        if pregunta.lower() in ["salir", "exit"]:
            break
        respuesta = agente.invoke(pregunta)
        print(f"\n🤖 Agente:\n{respuesta}")

if __name__ == "__main__":
    main()
