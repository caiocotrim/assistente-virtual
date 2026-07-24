import os

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

import json

import shutil

from config import embeddings


# Pasta onde os índices de cache semântico ficam salvos (um por curso)
CACHE_DIR = "cache_semantico"

RESPOSTAS_DIR = "respostas"

# Limiar de distância (FAISS/L2) para considerar a pergunta "igual" a uma já cacheada.
# Quanto MENOR o valor, mais rígida é a exigência de similaridade.
# Esse valor pode precisar de ajuste conforme os testes.
LIMIAR_SIMILARIDADE = 0.15


class SemanticCache:
    """
    Cache semântico de perguntas e respostas.

    Para cada curso, mantém um índice FAISS próprio, onde:
    - page_content = pergunta original
    - metadata["resposta"] = resposta já aprovada para aquela pergunta
    """

    def __init__(self):

        self.indices = {}

        os.makedirs(CACHE_DIR, exist_ok=True)

        self.reconstruir_todos_indices()

    def _caminho_json(self, curso):

        return os.path.join(
            RESPOSTAS_DIR,
            curso,
            f"resp-{curso}.json"
        )


    def _carregar_json(self, curso):

        caminho = self._caminho_json(curso)

        os.makedirs(
            os.path.dirname(caminho),
            exist_ok=True
        )

        if not os.path.exists(caminho):

            with open(
                caminho,
                "w",
                encoding="utf-8"
            ) as arquivo:

                json.dump(
                    [],
                    arquivo,
                    ensure_ascii=False,
                    indent=4
                )

            return []

        with open(
            caminho,
            "r",
            encoding="utf-8"
        ) as arquivo:

            conteudo = arquivo.read().strip()

            if not conteudo:
                return []

            return json.loads(conteudo)


    def _salvar_json(self, curso, dados):

        caminho = self._caminho_json(curso)

        with open(
            caminho,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                dados,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

    def _reconstruir_indice(self, curso):

        dados = self._carregar_json(curso)

        if not dados:
            caminho = self._caminho_indice(curso)

            if os.path.exists(caminho):

                shutil.rmtree(caminho)

            self.indices.pop(curso, None)

            print(f"[CACHE] Índice do curso '{curso}' removido (JSON vazio).")

            return

        documentos = []

        for item in dados:

            documentos.append(

                Document(

                    page_content=item["pergunta"],

                    metadata={

                        "resposta": item["resposta"]

                    }

                )

            )

        indice = FAISS.from_documents(
            documentos,
            embeddings
        )

        caminho = self._caminho_indice(curso)

        indice.save_local(caminho)

        self.indices[curso] = indice

        print(f"[CACHE] Índice reconstruído para o curso '{curso}'.")

    def reconstruir_todos_indices(self):

        print("[CACHE] Reconstruindo índices do cache...")

        if not os.path.exists(RESPOSTAS_DIR):

            print("[CACHE] Pasta de respostas não encontrada.")

            return

        for curso in os.listdir(RESPOSTAS_DIR):

            caminho = os.path.join(
                RESPOSTAS_DIR,
                curso
            )

            if os.path.isdir(caminho):

                self._reconstruir_indice(curso)

        print("[CACHE] Todos os índices foram reconstruídos.")
    

    # Caminho do índice de cache de um curso específico
    def _caminho_indice(self, curso):

        return os.path.join(CACHE_DIR, curso)

    # Carrega (ou retorna do cache em memória) o índice FAISS de um curso
    def _carregar_indice(self, curso):

        if curso in self.indices:
            return self.indices[curso]

        caminho = self._caminho_indice(curso)

        if os.path.exists(caminho):

            print(f"[CACHE] Carregando índice de cache existente: {caminho}")

            indice = FAISS.load_local(
                caminho,
                embeddings,
                allow_dangerous_deserialization=True
            )

            self.indices[curso] = indice

            return indice

        return None

    # Busca uma pergunta similar já cacheada para o curso informado
    def buscar(self, pergunta, curso):

        indice = self._carregar_indice(curso)

        if indice is None:
            return None

        resultados = indice.similarity_search_with_score(
            pergunta,
            k=1
        )

        if not resultados:
            return None

        documento, score = resultados[0]

        print(f"[CACHE] Distância encontrada: {score}")

        if score <= LIMIAR_SIMILARIDADE:
            return documento.metadata.get("resposta")

        return None

    # Salva uma nova pergunta/resposta aprovada no cache do curso
    def salvar(self, pergunta, resposta, curso):
        dados = self._carregar_json(curso)

        for item in dados:
            if item["pergunta"] == pergunta:
                print(f"[CACHE] Pergunta já existe no JSON do curso '{curso}'.")
                return

        dados.append({

            "pergunta": pergunta,

            "resposta": resposta

        })

        self._salvar_json(
            curso,
            dados
        )
        
        self._reconstruir_indice(curso)

        print(f"[CACHE] Pergunta/resposta salva no cache do curso '{curso}'.")


# Instância única utilizada pelo restante do sistema (rag.py)
cache = SemanticCache()