from typing import _TypedDict, Annotated,Sequence
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI, HarmCategory, HarmBlockThreshold
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.vectorstores import FAISS
from langchain.tools import tool
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import os
from tavily import TavilyClient
import sqlite3

load_dotenv()

# 1. Instanciar a memória
memory = MemorySaver()

tavily_client = TavilyClient(os.getenv("TAVILY_API_KEY"))


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.5,
    max_tokens=2024,
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    },
)


llm_judge = HuggingFaceEndpoint(
    model="microsoft/Phi-3.5-mini-instruct",
    api_key=os.getenv("HUGGING_FACE_API_KEY"),
    temperature=0.1,
    max_output_tokens=512,                                                             
)


@tool
def tavily_search(query: str):
    """
    Consulta a internet para trazer informações como: Tendencias atuais, noticias, principais
    conteudos mais buscado hoje em dia. 
    Para informações em tempo real.
    """
    contexto = tavily_client.search(query=query)
    return contexto



embeddings_locais = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = FAISS.load_local("db", embeddings_locais, allow_dangerous_deserialization=True)

@tool
def buscar_base_conteudo_gaby(query: str):
    """
    Acesso ao cérebro/base de conhecimento interna da Nyx. 
    Contém diretrizes, conceitos técnicos, preferências da Gaby, 
    identidade visual e marca registrada. 
    Use sempre que precisar de informações que não estão na internet.
    """
    docs = vectorstore.similarity_search(query, k=3)
    contexto = "n\n".join([doc.page_content for doc in docs])
    return contexto



@tool
def agent_text_to_sql(query: str):
    """
    Esta ferramenta interage com um banco de dados 
    SQLite para gerenciar vídeos de YouTube e TikTok.
    A tabela se chama 'videos' e possui as colunas:
    id, titulo, data_entrega, status, plataforma. 
    Use esta ferramenta para inserir novas ideias,
    consultar prazos ou atualizar o status de gravação.
    
    """
    criar_conexao = sqlite3.connect("banco_videos.db")
    print(os.path.abspath("banco_videos.db"))
    try: 
        cursor = criar_conexao.cursor()
        if "SELECT" in query.upper():
            cursor.execute(query)
            result = cursor.fetchall()
            return f"Resultado da consulta: {result}"
        
        elif "INSERT" in query or "UPDATE" in query:
            cursor.execute(query)
            criar_conexao.commit()
            return f"Operação realizada: {cursor.rowcount} linha(s) afetada(s)"
          
        else:
            cursor.execute(query)
            criar_conexao.commit()
            return f"Operação de exclusão realizada {cursor.rowcount}"
    except Exception as e:
        return f"Erro: {e}"
    finally:
        criar_conexao.close()


# Tive que colocar as ferramentas antes para reconhcer elas depois na função de chamar llm
tools = [
        tavily_search,
        buscar_base_conteudo_gaby,
        agent_text_to_sql,
    ]

tool_node = ToolNode(tools)

llm_com_tools = llm.bind_tools(tools)

class AgentState(_TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

"""
    class RouterDecision(BaseModel):
    next_step: str = Field(description="O proximo nó a seguir: 'buscar_base_conteudo_gaby' ou 'tavily_search'")
    reasoning: str = Field(description="A explicação do porquê escolheu esse caminho")
"""
#Inicei com roteamento manual, mas evolui para Native tool Calling para ganhar perfomance.

def chamar_llm(state: AgentState) -> AgentState:

    system_propmt = """
        Voce é um agente pessoal que se chama Nyx, assistente pessoal da Gabryelle Kirmayr
        e deve escolher qual tool usar de acordo
        com a pergunta do usuário.
        Voce deve ter: Humor = 70%
                        Intelgência = 101%
                        Genorisade = 90%
        Voce deve ser amigavel e informal dependendo do assunto.
        Caso nao precise de nenhuma tool, gere a respota.
        Voce deve pensar profudamente.
        A agente NYX deve:
        - Priorizar crescimento estratégico sobre validação externa.
        - Sugerir decisões com visão internacional.
        - Reforçar disciplina e consistência.
        - Organizar ideias em frameworks claros.
        - Pensar como arquiteta de sistemas, não como criadora improvisada.
        Você possui tres ferramenta ferramentas: uma para buscas na internet (Tavily) e outra para acessar sua base de conhecimento interna sobre a Gaby
        ,  e um uma ferramenta de SQL. Quando o usario quiser salvar uma ideia ou ver prazos,
        escreva o comando SQL correto e chame a ferramenta
        """
    # Ela deve tem tres caminhos, responder agora, caso a mensagem seja basica, escolher verificar na base, ou fazer uma pesquisa
    messages = [SystemMessage(content=system_propmt)] + state['messages']

    llm_result = llm_com_tools.invoke(messages)
    return {'messages': [llm_result]}

def llm_as_judge(state: AgentState) -> AgentState:
    
    pergunta_usuario = state['messages'][0].content
    
    reposta_bruta = state['messages'][-1].content

    propmt_juiz = f"""
    Você é o módulo de controle de qualidade da IA Nyx.
    Sua missão é avaliar se a resposta abaixo é segura,
    precisa e resolve a dúvida do usuário.
    Sua tarefa é avaliar:
    1. Se for SQL: O comando é apenas de leitura ou escrita permitida?
    (Evite DROP/DELETE sem filtro).
    2. Se for RAG: A informação realmente existe no contexto ou a IA inventou?
    Pergunta do usuário: {pergunta_usuario}
    Resposta da IA: {reposta_bruta}

    Se a resposta for insuficinete ou errada, peça para o agente reformular.
    Se estiver perfeita, aprove.
    Responda em formato JSON:
    {{"aprovado": true/false, "feedback": "motivo", "resposta_final": "texto formatado para o usuário"}}
    """
    resultado = llm.invoke(propmt_juiz)
    return {"messages": [SystemMessage(content=f"Veredito do Juiz: {resultado.content}")]}
    


builder = StateGraph(
    AgentState, context_schema=None, input_schema=AgentState, output_schema=AgentState
) # Importante para passar o runtime dos nodes: configs, contextos

builder.add_node("chamar_llm", chamar_llm)
builder.add_node("tools", tool_node)
builder.add_node("llm_judge", llm_as_judge)
builder.add_edge(START, "chamar_llm")
builder.add_conditional_edges(
    "chamar_llm",
    tools_condition
)
builder.add_edge("tools", "llm_judge")
builder.add_edge("llm_judge", "chamar_llm")
builder.add_edge("chamar_llm", END)


# 5 Compilar meu grafo
graph = builder.compile(checkpointer=memory)

''' 3. O Identificador da Conversa (thread_id)
A memória no LangGraph funciona por "pastas". 
Cada conversa precisa de um thread_id. Se você usar o mesmo ID,
 a Nyx lembra de tudo; se mudar o ID, é um chat novo.
'''
if __name__ == '__main__':
    # 6 Usar o grafo
    # Configuração da "sessão" do chat
    config = {"configurable": {"thread_id": "conversa_da_gaby"}}

    print("--- 🤖 Nyx Iniciada! (Digite 'sair' para encerrar) ---")
    

    while True:
        pergunta = input("\nVocê: ")
    
        if pergunta.lower() in ['sair', 'exit', 'quit']:
             break
        
        inputs = {"messages": [HumanMessage(content=pergunta)]}


        resultadp = graph.invoke(inputs, config=config)

        ultima_msg = resultadp["messages"][-1]

        if isinstance(ultima_msg.content, list):
            texto_limpo = "".join([p['text'] for p in ultima_msg.content if 'text' in p])
        else:
            texto_limpo = ultima_msg.content

        print("\n--- 🤖 Nyx diz: ---")
        print(texto_limpo)
                            
                    
                    

