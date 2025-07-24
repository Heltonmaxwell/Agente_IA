# agents.py

import os
from dotenv import load_dotenv

# Carrega variáveis do .env (opcional)
#dotenv_path = r"C:/Users/admin/Documents/Python/Agente_IA/.env"
#dotenv_loaded = load_dotenv(dotenv_path)
#print("dotenv carregado?", dotenv_loaded)

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import tool

from scrapper import get_text_from_url

# Função que usa o modelo local via Ollama
def get_response_from_local_model(message):
    llm = ChatOllama(model="gemma:2b")  # Modelo local
    response = llm.invoke(message)
    return response.content

# Ferramenta: Leitura de documentação
@tool
def documentation_tool(url: str, question: str) -> str:

    """Lê uma documentação da URL e responde à pergunta com base no conteúdo extraído."""
    context = get_text_from_url(url)

    messages = [
        SystemMessage(content="Você é um assistente de programação que deve explicar a documentação de forma simples."),
        HumanMessage(content=f"Documentação: {context} \n\n {question}")
    ]

    response = get_response_from_local_model(messages)
    return response

# Ferramenta: Formatador Black via modelo local
@tool
def black_formatter_tool(path: str) -> str:
    """Lê um arquivo Python, pede ao modelo para formatar, e salva o resultado."""
    try:
        # 1. Ler o arquivo
        with open(path, "r", encoding="utf-8") as f:
            codigo_original = f.read()

        # 2. Mensagens para o modelo pedir a formatação
        messages = [
            SystemMessage(content="Você é um assistente que formata código Python seguindo o estilo do Black."),
            HumanMessage(content=f"Formate este código Python:\n{codigo_original}")
        ]

        # 3. Chamar o modelo local
        response = get_response_from_local_model(messages)

        # 4. Salvar o código formatado no arquivo
        with open(path, "w", encoding="utf-8") as f:
            f.write(response)

        return "Código formatado e salvo com sucesso!"

    except Exception as e:
        return f"Erro na formatação: {str(e)}"

# Ferramentas disponíveis para o agente
toolkit = [documentation_tool, black_formatter_tool]

# Modelo local via Ollama
llm = ChatOllama(model="gemma:2b", temperature=0)

# Template do prompt do agente
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """
        Você é um programa assistente. Use suas ferramentas para responder perguntas. 
        Se você não tiver ferramentas para responder à pergunta, apenas diga que não tem essa informação disponível no momento.

        Retorne apenas as respostas.
        """),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ]
)

# Criação do agente
agent = create_openai_tools_agent(llm, toolkit, prompt)
agent_executor = AgentExecutor(agent=agent, tools=toolkit, verbose=True)

# Teste básico
#result = agent_executor.invoke({"input": r"Eu quero que você formate esse meu código python. path: C:\Users\admin\Documents\Python\Agente_IA\scrapper.py"})
result = agent_executor.invoke({"input": "Eu quero que você formate esse meu código python. path: C:/Users/admin/Documents/Python/Agente_IA/scrapper.py"})

print(result)
