import gradio

from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

load_dotenv()

loader = DirectoryLoader("base-de-dados/txt-files/bsi", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt = loader.load()

embeddings = OpenAIEmbeddings()
base_vetores = FAISS.from_documents(docs_txt, embeddings)
retriever = base_vetores.as_retriever()

llm = ChatOpenAI()

prompt_padrao="""
Você é um assistente virtual acadêmico especializado em fornecer informações sobre os cursos oferecidos pelo Instituto Federal da Bahia (IFBA) - Campus Vitória da Conquista. 
Utilize as informações fornecidas para responder às perguntas dos usuários de forma clara e precisa.

Contexto: {context}
Pergunta: {question}
"""
prompt = ChatPromptTemplate.from_template(prompt_padrao)

chain = ({"context": retriever, "question": RunnablePassthrough()} | prompt | llm)

def responder(mensagem, historico): 
    retorno_chain = chain.invoke(mensagem)
    resposta = retorno_chain.content
    return resposta

interface = gradio.ChatInterface(fn=responder)
interface.launch() 