from typing import _TypedDict, Annotated, Literal,Sequence
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import Messages
from langchain_google_genai import ChatGoogleGenerativeAI
from rich import print
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY")   
)

# NÃO PRECISA FAZER ISSO
def reducer(a: Messages, b: Messages) -> Messages : # mesmo protocolo da linha 15
    return add_messages(a, b) # para mostar o caminho da mensagem

# 1 Define o meu state
class AgenteState(_TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages, reducer] # Nunca alterar estado diretamnete

# 2 Definir os nodes
def chama_llm(state: AgenteState) -> AgenteState:
    llm_result = llm.invoke(state['messages'])
    return {'messages': [llm_result] + state['messages']}

# 3 criar o state graph

builder = StateGraph(
    AgenteState, context_schema=None, input_schema=AgenteState, output_schema=AgenteState
) # Importante para passar o runtime dos nodes: configs, contextos

# 4 Adicionar os nodes
builder.add_node(chama_llm, "chama_llm")
builder.add_edge(START, "chama_llm")
builder.add_edge("chama_llm", END)  

# 5 Compilar meu grafo

graph = builder.compile()

if __name__ == '__main__':
    # 6 Usar o grafo
    human_message = HumanMessage("Olá meu nome é gaby, tudp bem:!")
    result = graph.invoke({'messages': [human_message]})
    print(f"",result)

