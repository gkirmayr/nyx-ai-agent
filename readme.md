# 🤖 Nyx: AI Agent Architect

A **Nyx** é uma Prova de Conceito (POC) de uma assistente pessoal inteligente desenvolvida sob a ótica de **Arquitetura de Sistemas**. O agente utiliza orquestração avançada para realizar tarefas complexas, integrando bases de dados relacionais, busca semântica em documentos e pesquisa web em tempo real.

---

## 🎯 Visão Geral

Diferente de chatbots convencionais, a Nyx opera como um **Agente ReAct** (Reasoning and Acting). Ela não apenas responde perguntas, mas planeja ações e executa ferramentas para resolver problemas de forma autônoma e segura.

## 🚀 Funcionalidades Principais

* **📊 Text-to-SQL Engine:** Interface de linguagem natural para bancos de dados SQLite. Permite a gestão de conteúdos e cronogramas sem a necessidade de comandos manuais.
* **🧠 Knowledge Retrieval (RAG):** Sistema de busca semântica integrado a uma base de conhecimento técnica e pessoal utilizando **FAISS**.
* **🌐 Real-time Web Search:** Integração com **Tavily API** para captura de tendências e notícias atualizadas.
* **⚖️ Governance (LLM-as-Judge):** Camada de segurança que valida a integridade das queries SQL e a veracidade das respostas do RAG antes da exibição ao usuário.

---

## 🏗️ Arquitetura do Sistema

O projeto utiliza um **Grafo de Estados Cíclico** construído com **LangGraph**, permitindo ciclos de retroalimentação e validação entre os nós.

### 🛠️ Stack Tecnológica

| Componente | Tecnologia |
| :--- | :--- |
| **Orquestrador** | LangGraph |
| **Modelos de Linguagem** | Google Gemini 2.5 Flash / Phi-3.5 (Judge) |
| **Vector Store** | FAISS |
| **Banco de Dados** | SQLite |
| **Embeddings** | HuggingFace (`all-MiniLM-L6-v2`) |

---

## 🔧 Configuração e Instalação

### Pré-requisitos
- Python 3.10 ou superior
- Chaves de API: Google Gemini e Tavily e HuggingFace


### Instalação
1. Clone o repositório:
   ```bash
   git clone [https://github.com/gkirmayr/nyx-ai-agent.git](https://github.com/gkirmayr/nyx-ai-agent.git)
Instale as dependências:

Bash
pip install -r requirements.txt
Configure o arquivo .env:

Snippet de código
GOOGLE_API_KEY=sua_chave_aqui
TAVILY_API_KEY=sua_chave_aqui
🛡️ Camada de Segurança e Ética
A Nyx foi desenhada com princípios de IA Responsável:

Sanitização de Queries: O modelo Juiz bloqueia comandos de destruição de dados (DROP, DELETE em massa).

Anti-Alucinação: Validação de contexto para garantir que informações do RAG sejam fundamentadas nos documentos fornecidos.

👩‍💻 Autora
Gabryelle Kirmayr
Estagiária de Desenvolvimento na NTT DATA Inc.
Foco em se tornar Data Scientist / AI Engineer.



Todos os direitos reservados.
Este repositório contém uma POC desenvolvida por Gabryelle Kirmayr para fins de demonstração técnica e evolução profissional.

---

