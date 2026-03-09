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
# Loader dos cursos abaixos estão comentados pois ainda não há dados tratados para eles
"""
loader_eletrica = DirectoryLoader("../../base-de-dados/dados-tratados/eletrica", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_eletrica = loader_eletrica.load()

loader_quimica = DirectoryLoader("../../base-de-dados/dados-tratados/quimica", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_quimica = loader_quimica.load()

loader_geral = DirectoryLoader("../../base-de-dados/dados-tratados/geral", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_geral = loader_geral.load()
"""

embeddings = OpenAIEmbeddings()

faiss_bsi = FAISS.from_documents(docs_txt_bsi, embeddings)
faiss_civil = FAISS.from_documents(docs_txt_civil, embeddings)
faiss_ambiental = FAISS.from_documents(docs_txt_ambiental, embeddings)
# Base de dados dos cursos abaixos estão comentados pois ainda não há dados tratados para eles
"""
faiss_eletrica = FAISS.from_documents(docs_txt_eletrica, embeddings)
faiss_quimica = FAISS.from_documents(docs_txt_quimica, embeddings)
faiss_geral = FAISS.from_documents(docs_txt_geral, embeddings)
"""

retriever_bsi = faiss_bsi.as_retriever()
retriever_civil = faiss_civil.as_retriever()
retriever_ambiental = faiss_ambiental.as_retriever()
# Retrievers dos cursos abaixos estão comentados pois ainda não há dados tratados para eles
"""
retriever_eletrica = faiss_eletrica.as_retriever()
retriever_quimica = faiss_quimica.as_retriever()
retriever_geral = faiss_geral.as_retriever()
"""

llm = ChatOpenAI()

prompt_padrao="""
Você é um assistente virtual acadêmico especializado em fornecer informações sobre os cursos oferecidos pelo Instituto Federal da Bahia (IFBA) - Campus Vitória da Conquista. 
Utilize as informações fornecidas para responder às perguntas dos usuários de forma clara e precisa. 
Caso seja uma informação específica sobre algum curso e usuário não tenha especificado qual curso deseja obter a informação, não responda a pergunta e solicite que o usuário informe o curso desejado para que você possa responder.

Contexto: {context}
Pergunta: {question}
"""
prompt = ChatPromptTemplate.from_template(prompt_padrao)

def escolher_retriever(mensagem):
    msg = mensagem.lower()
    if "bsi" in msg or "sistemas de informação" in msg or "sistemas" in msg or "si" in msg or "informática" in msg:
        return retriever_bsi
    if "civil" in msg or "engenharia civil" in msg or "eng civil" in msg or "eng. civil" in msg:
        return retriever_civil    
    if "ambiental" in msg or "engenharia ambiental" in msg or "eng ambiental" in msg or "eng. ambiental" in msg:
        return retriever_ambiental
    # Retrievers dos cursos abaixos estão comentados pois ainda não há dados tratados para eles
    """
    if "elétrica" in msg or "engenharia elétrica" in msg or "eng elétrica" in msg or "eng. elétrica" in msg:
        return retriever_eletrica
    if "química" in msg or "engenharia química" in msg or "eng química" in msg or "eng. química" in msg:
        return retriever_quimica
    else:
        return retriever_geral
    """    
    return None

def responder(mensagem, historico):

    retriever = escolher_retriever(mensagem)

    if retriever is None:
        return "Não consegui compreender sua mensagem. Por favor, seja um pouco mais específico. Caso sua dúvida tenha haver com algum curso, deixe o nome do curso explícito na mensagem."

    chain = ({"context": retriever, "question": RunnablePassthrough()} | prompt | llm)

    resposta = chain.invoke(mensagem)
    return resposta.content


interface = gradio.ChatInterface(fn=responder)
interface.launch() 
