import gradio
import json
import os
import re 

from dotenv import load_dotenv

from datetime import datetime

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

PDFS = {
    "bsi": "../../base-de-dados/dados-brutos/bsi/ppc_bsi.pdf",

    "engenharia_civil": "../../base-de-dados/dados-brutos/civil/ppc_civil.pdf",

    "engenharia_ambiental": "../../base-de-dados/dados-brutos/ambiental/ppc_ambiental.pdf",

    "engenharia_eletrica": "../../base-de-dados/dados-brutos/eletrica/ppc_eletrica.pdf",

    "licenciatura_quimica": "../../base-de-dados/dados-brutos/quimica/ppc_quimica.pdf",
}

loader_bsi = DirectoryLoader("../../base-de-dados/dados-tratados/bsi", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_bsi = loader_bsi.load()
docs_txt_bsi = text_splitter.split_documents(docs_txt_bsi)

loader_civil = DirectoryLoader("../../base-de-dados/dados-tratados/civil", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_civil = loader_civil.load()
docs_txt_civil = text_splitter.split_documents(docs_txt_civil)

loader_ambiental = DirectoryLoader("../../base-de-dados/dados-tratados/ambiental", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_ambiental = loader_ambiental.load()
docs_txt_ambiental = text_splitter.split_documents(docs_txt_ambiental)

loader_eletrica = DirectoryLoader("../../base-de-dados/dados-tratados/eletrica", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_eletrica = loader_eletrica.load()
docs_txt_eletrica = text_splitter.split_documents(docs_txt_eletrica)

loader_quimica = DirectoryLoader("../../base-de-dados/dados-tratados/quimica", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_quimica = loader_quimica.load()
docs_txt_quimica = text_splitter.split_documents(docs_txt_quimica)

loader_geral = DirectoryLoader("../../base-de-dados/dados-tratados/geral", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_geral = loader_geral.load()
docs_txt_geral = text_splitter.split_documents(docs_txt_geral)

embeddings = OpenAIEmbeddings()

def carregar_criar_faiss(path, docs, embeddings):
    if os.path.exists(path):
        print(f"[INFO] Carregando índice existente: {path}")
        return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
    else:
        print(f"[INFO] Criando novo índice: {path}")
        index = FAISS.from_documents(docs, embeddings)
        index.save_local(path)
        return index

faiss_bsi = carregar_criar_faiss("indices/bsi", docs_txt_bsi, embeddings)
faiss_civil = carregar_criar_faiss("indices/civil", docs_txt_civil, embeddings)
faiss_ambiental = carregar_criar_faiss("indices/ambiental", docs_txt_ambiental, embeddings)
faiss_eletrica = carregar_criar_faiss("indices/eletrica", docs_txt_eletrica, embeddings)
faiss_quimica = carregar_criar_faiss("indices/quimica", docs_txt_quimica, embeddings)
faiss_geral = carregar_criar_faiss("indices/geral", docs_txt_geral, embeddings)

retriever_bsi = faiss_bsi.as_retriever(search_kwargs={"k": 8})
retriever_civil = faiss_civil.as_retriever(search_kwargs={"k": 8})
retriever_ambiental = faiss_ambiental.as_retriever(search_kwargs={"k": 8})
retriever_eletrica = faiss_eletrica.as_retriever(search_kwargs={"k": 8})
retriever_quimica = faiss_quimica.as_retriever(search_kwargs={"k": 8})
retriever_geral = faiss_geral.as_retriever(search_kwargs={"k": 8})

llm = ChatOpenAI()

prompt_curso="""
Você é um classificador de perguntas acadêmicas do IFBA – Campus Vitória da Conquista.

Sua tarefa é identificar a qual curso a pergunta do usuário se refere.
Considere linguagem natural, abreviações e sinônimos comuns usados por estudantes.

Classifique a pergunta em APENAS UMA das categorias abaixo:

- bsi: Bacharelado em Sistemas de Informação  
Exemplos de termos relacionados:
"bsi", "sistemas de informação", "curso de ti", "computação", "sistemas"

- engenharia_civil: Engenharia Civil  
Exemplos:
"civil", "engenharia civil", "curso de civil"

- engenharia_ambiental: Engenharia Ambiental  
Exemplos:
"ambiental", "engenharia ambiental", "meio ambiente"

- engenharia_eletrica: Engenharia Elétrica  
Exemplos:
"elétrica", "engenharia elétrica", "curso de elétrica"

- licenciatura_quimica: Licenciatura em Química  
Exemplos:
"química", "licenciatura em química", "curso de química"

- geral: Use APENAS se a pergunta não se referir a nenhum curso específico.
Exemplos:
informações institucionais, campus, calendário acadêmico, eventos, matrícula, biblioteca.

REGRAS IMPORTANTES:
- Se o curso estiver implícito na pergunta, escolha o curso correspondente.
- NÃO peça esclarecimentos.
- NÃO explique sua resposta.
- NÃO invente categorias.
- Responda SOMENTE com um dos rótulos abaixo:
bsi  
engenharia_civil  
engenharia_ambiental  
engenharia_eletrica  
licenciatura_quimica  
geral  

Pergunta do usuário:
{question}
"""
prompt_curso_definido = ChatPromptTemplate.from_template(prompt_curso)

def classificar_retriever(pergunta):
    chain_curso = prompt_curso_definido | llm
    resposta = chain_curso.invoke({"question": pergunta})
    resposta_formatada = resposta.content.strip().lower()

    if resposta_formatada == "bsi":
        return retriever_bsi, "bsi"
    elif resposta_formatada == "engenharia_civil":
        return retriever_civil, "engenharia_civil"
    elif resposta_formatada == "engenharia_ambiental":
        return retriever_ambiental, "engenharia_ambiental"
    elif resposta_formatada == "engenharia_eletrica":
        return retriever_eletrica, "engenharia_eletrica"
    elif resposta_formatada == "licenciatura_quimica":
        return retriever_quimica, "licenciatura_quimica"
    elif resposta_formatada == "geral":
        return retriever_geral, "geral"

def usuario_pediu_ppc(texto):
    texto = texto.lower()

    palavras_chave = [
        "ppc",
        "projeto pedagógico",
        "projeto pedagogico",
        "pdf",
        "documento do curso",
        "me envie",
        "envie",
        "mande",
        "baixar"
    ]

    return any(p in texto for p in palavras_chave)

prompt_memoria="""
Você é um classificador de contexto. 

Sua tarefa é decidir se a PERGUNTA ATUAL depende do HISTÓRICO da conversa.

Responda APENAS com:
SIM
ou
NAO

Regras:
- Responda SIM se a pergunta fizer referência a algo anterior (ex: "isso", "esse curso", "também", "ele", etc.)
- Responda NAO se a pergunta for independente e puder ser entendida sozinha
- NÃO explique
- NÃO escreva nada além de SIM ou NAO

Histórico:
{history}

Pergunta atual:
{question}
"""
prompt_memoria_template = ChatPromptTemplate.from_template(prompt_memoria)

chain_memoria = prompt_memoria_template | llm
def decidir_uso_memoria(pergunta, historico):
    if not historico:
        return False
    
    historico_formatado=""
    for msg in historico:
        role = "Usuário" if msg["role"] == "user" else "Assistente"
        historico_formatado += f"{role}: {msg['content']}\n"

    resposta = chain_memoria.invoke({
        "history": historico_formatado,
        "question": pergunta
    })

    return resposta.content.strip().upper() == "SIM"

prompt_padrao="""
Você é um assistente acadêmico do IFBA.

Responda a pergunta utilizando APENAS as informações do contexto fornecido.
A ÚNICA excessão é mensagem de saudação como: oi, olá, bom dia, boa tarde, boa noite e etc. Nesse ÚNICO contexto, você pode responder com a devida educação.

REGRAS IMPORTANTES:
- Não invente informações
- Se a resposta não estiver no contexto, diga claramente:
  "Não encontrei essa informação nos documentos disponíveis"
- Seja direto e objetivo
- Não use conhecimento externo
- O histórico já foi previamente filtrado:
  - Se estiver vazio, ignore
  - Se estiver preenchido, use como apoio

Histórico:
{history}

Contexto:
{context}

Pergunta:
{question}
"""
prompt = ChatPromptTemplate.from_template(prompt_padrao)


prompt_rerank = """
Você é um assistente que seleciona os documentos mais relevantes para responder uma pergunta.

Sua tarefa:
- Avaliar os documentos abaixo
- Selecionar os 3 MAIS relevantes para responder a pergunta

Retorne APENAS os números dos documentos mais relevantes, separados por vírgula.

Pergunta:
{question}

Documentos:
{docs}
"""
prompt_rerank_template = ChatPromptTemplate.from_template(prompt_rerank)
chain_rerank = prompt_rerank_template | llm

def responder(mensagem, historico):

    resultado = classificar_retriever(mensagem)
    if not resultado:
        return "Desculpe, não consegui identificar à sua pergunta. Por favor, caso sua dúvida seja relacionada à algum curso, especifique o curso para que eu possa ajudar melhor. Caso não seja, reformule melhor a sua pergunta."
    
    retriever, curso_classificado = resultado

    if usuario_pediu_ppc(mensagem):

        caminho_pdf = PDFS.get(curso_classificado)

        if caminho_pdf and os.path.exists(caminho_pdf):

            return {
                "text": "Segue o Projeto Pedagógico do Curso solicitado.",
                "files": [caminho_pdf]
            }

        return "Não encontrei o PPC desse curso."

    docs_recuperados = retriever.invoke(mensagem)
    docs_formatados = ""
    for i, doc in enumerate(docs_recuperados):
        docs_formatados += f"[{i}] {doc.page_content}\n\n"
    
    if len(docs_recuperados) > 4:
        resposta_rerank = chain_rerank.invoke({
            "question": mensagem,
            "docs": docs_formatados
        })

        try:
            indices = re.findall(r'\d+', resposta_rerank.content)
            indices = [int(i) for i in indices]

            docs_filtrados = [
                docs_recuperados[i]
                for i in indices
                if i < len(docs_recuperados)
            ]

            if not docs_filtrados:
                docs_filtrados = docs_recuperados[:3]

        except:
            docs_filtrados = docs_recuperados[:3]

    else:
        docs_filtrados = docs_recuperados

    contexto = "\n\n".join([doc.page_content for doc in docs_filtrados])

    usar_memoria_flag = decidir_uso_memoria(mensagem, historico)
    historico_formatado = ""
    if usar_memoria_flag:
        for msg in historico:
            role = "Usuário" if msg["role"] == "user" else "Assistente"
            historico_formatado += f"{role}: {msg['content']}\n"

    chain = (prompt | llm)
    resposta = chain.invoke({
        "context": contexto,
        "question": mensagem,
        "history": historico_formatado
    })

    log = {
        "timestamp": datetime.now().isoformat(),
        "pergunta": mensagem,
        "curso_classificado": curso_classificado,
        "documentos_recuperados": [
            {
                "conteudo": doc.page_content[:500],
                "metadata": doc.metadata
            }
            for doc in docs_recuperados
        ],
        "documentos_usados": [
            {
                "conteudo": doc.page_content[:500],
                "metadata": doc.metadata
            }
            for doc in docs_filtrados
        ],
        "resposta": resposta.content
    }

    with open("../../logs/logs.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")

    return resposta.content

interface = gradio.ChatInterface(fn=responder, type="messages")
interface.launch()