import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

load_dotenv()

# Leer claves
openai_api_key = os.getenv("OPENAI_API_KEY")
serpapi_api_key = os.getenv("SERPAPI_API_KEY")

if not openai_api_key:
    raise ValueError("No se encontró la variable OPENAI_API_KEY en el archivo .env")
if not serpapi_api_key:
    raise ValueError("No se encontró la variable SERPAPI_API_KEY en el archivo .env")

os.environ["OPENAI_API_KEY"] = openai_api_key
os.environ["SERPAPI_API_KEY"] = serpapi_api_key

# Cargar índice vectorial
def cargar_vectordb():
    path = "vector_index/"
    if not os.path.exists(path):
        raise FileNotFoundError("No se encontró el índice FAISS. Ejecuta primero indexador.py.")
    return FAISS.load_local(path, OpenAIEmbeddings(), allow_dangerous_deserialization=True)

# Herramienta de consulta local
def crear_tool_pdf(vectordb):
    def consulta(query: str) -> str:
        docs = vectordb.similarity_search(query, k=3)
        print("\n[DEBUG] Chunks recuperados por similarity_search:")
        for i, doc in enumerate(docs):
            print(f"--- Chunk {i+1} ---")
            print("Contenido:", doc.page_content[:300], "..." if len(doc.page_content) > 300 else "")
            if hasattr(doc, "metadata"):
                print("Metadatos:", doc.metadata)
            print("-------------------")
        if not docs:
            return "❌ No encontré información relevante en los documentos de pólizas."

        contenido = "\n\n".join([doc.page_content for doc in docs])
        if len(contenido.strip()) < 100:
            return "❌ No encontré información clara en los documentos."

        return f"✅ Esto fue lo que encontré en los documentos de pólizas:\n\n{contenido}"

    return Tool(
        name="ConsultaPDF",
        func=consulta,
        description="Consulta en la base de conocimiento de pólizas"
    )

# Herramienta web
def crear_tool_web():
    return Tool(
        name="BusquedaEnLinea",
        func=DuckDuckGoSearchRun().run,
        description="Consulta en internet como último recurso"
    )

# Agente con tono amable, respetuoso, profesional y limitado a pólizas
def responder(query: str, herramienta_pdf, herramienta_web, llm):
    system_prompt = (
        "Eres un agente de atención al cliente especializado en pólizas de seguros. "
        "Tu función es responder preguntas relacionadas únicamente con temas de seguros, pólizas, coberturas, derechos del asegurado, etc. "
        "Si el usuario hace preguntas que no tienen que ver con seguros, debes responder con cortesía indicando que no puedes ayudar con ese tema. "
        "Siempre debes responder con un tono amable, profesional, respetuoso y enfocado en ayudar al cliente."
    )
    
    ##Human prompt -- Template prompt
    ##template prompt
    
    respuesta_pdf = herramienta_pdf.run(query)

    if "No encontré" in respuesta_pdf:
        respuesta_web = herramienta_web.run(query)
        content = f"{system_prompt}\n\nPregunta del cliente: {query}\n\nRespuesta web:{respuesta_web}"
    else:
        content = f"{system_prompt}\n\nPregunta del cliente: {query}\n\nRespuesta en PDF:{respuesta_pdf}"

    print("\n[DEBUG] Prompt enviado al LLM:\n", content)
    response = llm.invoke(content)
    return response.content

def main():
    print("📚 Iniciando agente especializado en pólizas...")
    vectordb = cargar_vectordb()
    tool_pdf = crear_tool_pdf(vectordb)
    tool_web = crear_tool_web()
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)

    while True:
        pregunta = input("\n🧑 Tú: ")
        if pregunta.lower() in ["salir", "exit"]:
            break
        respuesta = responder(pregunta, tool_pdf, tool_web, llm)
        print(f"🤖 Agente:\n{respuesta}")

if __name__ == "__main__":
    main()
