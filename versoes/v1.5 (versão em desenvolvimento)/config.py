import os

from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


TOKEN = os.getenv("TELEGRAM_TOKEN")


# CONFIGURAÇÕES RAG

USAR_COMPRESSAO_CONTEXTO = True


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=4000,
    chunk_overlap=500,
    separators=[
        "\n\n",
        "\nDOCENTES",
        "\nDISCIPLINAS",
        "\nEMENTA",
        "\nOBJETIVOS",
        "\n",
        " ",
        ""
    ]
)


embeddings = OpenAIEmbeddings()


# Modelo principal para gerar respostas
llm = ChatOpenAI(
    model="gpt-4.1-mini"
)

# Modelo usado para filtrar contexto
# Pode ser trocado por um modelo menor futuramente
llm_compressor = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)


CURSOS = {

    "bsi": {
        "nome": "Bacharelado em Sistemas de Informação",
        "txt": "../../base-de-dados/dados-tratados/bsi",
        "indice": "indices/bsi",
        "pdf": "../../base-de-dados/dados-brutos/bsi/ppc_bsi.pdf",
        "ementas": "../../base-de-dados/dados-brutos/bsi/ementas"
    },


    "engenharia_civil": {
        "nome": "Engenharia Civil",
        "txt": "../../base-de-dados/dados-tratados/civil",
        "indice": "indices/civil",
        "pdf": "../../base-de-dados/dados-brutos/civil/ppc_civil.pdf",
        "ementas": "../../base-de-dados/dados-brutos/civil/ementas"
    },


    "engenharia_ambiental": {
        "nome": "Engenharia Ambiental",
        "txt": "../../base-de-dados/dados-tratados/ambiental",
        "indice": "indices/ambiental",
        "pdf": "../../base-de-dados/dados-brutos/ambiental/ppc_ambiental.pdf",
        "ementas": "../../base-de-dados/dados-brutos/ambiental/ementas"
    },


    "engenharia_eletrica": {
        "nome": "Engenharia Elétrica",
        "txt": "../../base-de-dados/dados-tratados/eletrica",
        "indice": "indices/eletrica",
        "pdf": "../../base-de-dados/dados-brutos/eletrica/ppc_eletrica.pdf",
        "ementas": "../../base-de-dados/dados-brutos/eletrica/ementas"
    },


    "licenciatura_quimica": {
        "nome": "Licenciatura em Química",
        "txt": "../../base-de-dados/dados-tratados/quimica",
        "indice": "indices/quimica",
        "pdf": "../../base-de-dados/dados-brutos/quimica/ppc_quimica.pdf",
        "ementas": "../../base-de-dados/dados-brutos/quimica/ementas"
    },


    "geral": {
        "nome": "Geral",
        "txt": "../../base-de-dados/dados-tratados/geral",
        "indice": "indices/geral",
        "pdf": None,
        "ementas": None
    }

}



def carregar_criar_faiss(path, docs):

    if os.path.exists(path):

        print(
            f"[INFO] Carregando índice existente: {path}"
        )

        return FAISS.load_local(
            path,
            embeddings,
            allow_dangerous_deserialization=True
        )


    print(
        f"[INFO] Criando índice: {path}"
    )


    indice = FAISS.from_documents(
        docs,
        embeddings
    )


    indice.save_local(path)


    return indice



retrievers = {}


for chave, curso in CURSOS.items():

    loader = DirectoryLoader(
        curso["txt"],
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={
            "encoding": "utf-8"
        }
    )


    documentos = loader.load()


    documentos = text_splitter.split_documents(
        documentos
    )


    indice = carregar_criar_faiss(
        curso["indice"],
        documentos
    )


    retrievers[chave] = indice.as_retriever(
        search_kwargs={
            "k": 8
        }
    )