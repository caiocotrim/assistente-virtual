import gradio

from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

load_dotenv()
loader_bsi = DirectoryLoader("../../base-de-dados/dados-tratados/bsi", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_bsi = loader_bsi.load()

loader_civil = DirectoryLoader("../../base-de-dados/dados-tratados/civil", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_civil = loader_civil.load()

loader_ambiental = DirectoryLoader("../../base-de-dados/dados-tratados/ambiental", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_ambiental = loader_ambiental.load()

loader_eletrica = DirectoryLoader("../../base-de-dados/dados-tratados/eletrica", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_eletrica = loader_eletrica.load()

loader_quimica = DirectoryLoader("../../base-de-dados/dados-tratados/quimica", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_quimica = loader_quimica.load()

loader_geral = DirectoryLoader("../../base-de-dados/dados-tratados/geral", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_geral = loader_geral.load()

embeddings = OpenAIEmbeddings()

faiss_bsi = FAISS.from_documents(docs_txt_bsi, embeddings)
faiss_civil = FAISS.from_documents(docs_txt_civil, embeddings)
faiss_ambiental = FAISS.from_documents(docs_txt_ambiental, embeddings)
faiss_eletrica = FAISS.from_documents(docs_txt_eletrica, embeddings)
faiss_quimica = FAISS.from_documents(docs_txt_quimica, embeddings)
faiss_geral = FAISS.from_documents(docs_txt_geral, embeddings)

retriever_bsi = faiss_bsi.as_retriever()
retriever_civil = faiss_civil.as_retriever()
retriever_ambiental = faiss_ambiental.as_retriever()
retriever_eletrica = faiss_eletrica.as_retriever()
retriever_quimica = faiss_quimica.as_retriever()
retriever_geral = faiss_geral.as_retriever()

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
        return retriever_bsi
    elif resposta_formatada == "engenharia_civil":
        return retriever_civil
    elif resposta_formatada == "engenharia_ambiental":
        return retriever_ambiental
    elif resposta_formatada == "engenharia_eletrica":
        return retriever_eletrica
    elif resposta_formatada == "licenciatura_quimica":
        return retriever_quimica
    elif resposta_formatada == "geral":
        return retriever_geral

prompt_padrao="""
Você é um assistente virtual acadêmico especializado em fornecer informações sobre os cursos oferecidos pelo Instituto Federal da Bahia (IFBA) - Campus Vitória da Conquista. 
Utilize as informações fornecidas para responder às perguntas dos usuários de forma clara e precisa.

Contexto: {context}
Pergunta: {question}
"""
prompt = ChatPromptTemplate.from_template(prompt_padrao)

def responder(mensagem, historico):

    retriever = classificar_retriever(mensagem)
    if not retriever:
        return "Desculpe, não consegui identificar à sua pergunta. Por favor, caso sua dúvida seja relacionada à algum curso, especifique o curso para que eu possa ajudar melhor. Caso não seja, reformule melhor a sua pergunta."
    
    chain = ({"context": retriever, "question": RunnablePassthrough()} | prompt | llm)
    resposta = chain.invoke(mensagem)
    return resposta.content


interface = gradio.ChatInterface(fn=responder)
interface.launch() 
