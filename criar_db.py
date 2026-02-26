from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter #importante para dividir textos grandes em pedaços menores
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

diretorio_atual = os.path.dirname(os.path.abspath(__file__))

google_api_key=os.getenv("GOOGLE_API_KEY")


pasta_base = os.path.join(diretorio_atual, "base")

def criar_db():

    documentos = carregar_documentos()
    
    chunks = dividir_em_chunks(documentos)

    vetoriar_chunks(chunks)
     
    print("DB criada com sucesso")

def carregar_documentos():
    carregador = PyPDFDirectoryLoader(pasta_base)
    documentos = carregador.load()
    return documentos

def dividir_em_chunks(documento):
    separar_documentos = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 100,
        length_function = len,
        add_start_index = True,
    )

    chunks = separar_documentos.split_documents(documento)
    print(f"Numero de chunks criados: {len(chunks)}")
    return chunks


def vetoriar_chunks(chunks):
    embeddings_locais = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    print("Iniciando a vetorização das chunks")

    try:
        vectorstore = FAISS.from_documents(
            documents=chunks,
            embedding=embeddings_locais,
        )    
        vectorstore.save_local("db", allow_dangerous_deserialization=True)
        print("Vetorização concluída com sucesso!")
    except Exception as e:
        print(f"Erro detalhado na API do Google: {e}")

    vectorstore.save_local("db")

    print("Vetorização concluída")

if __name__ == "__main__":
    criar_db()
          
