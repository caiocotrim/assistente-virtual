import os

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from config import embeddings


# Pasta onde os índices de cache semântico ficam salvos (um por curso)
CACHE_DIR = "cache_semantico"

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

        documento = Document(
            page_content=pergunta,
            metadata={
                "resposta": resposta
            }
        )

        indice = self._carregar_indice(curso)

        if indice is None:

            indice = FAISS.from_documents(
                [documento],
                embeddings
            )

        else:

            indice.add_documents([documento])

        caminho = self._caminho_indice(curso)

        indice.save_local(caminho)

        self.indices[curso] = indice

        print(f"[CACHE] Pergunta/resposta salva no cache do curso '{curso}'.")


# Instância única utilizada pelo restante do sistema (rag.py)
cache = SemanticCache()