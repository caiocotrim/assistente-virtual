import os
import json
import shutil

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from config import embeddings



# CONFIGURAÇÕES
CACHE_DIR = "cache_semantico"

RESPOSTAS_DIR = "respostas"


# Quanto menor, mais rígida a comparação
LIMIAR_SIMILARIDADE = 0.15



class SemanticCache:

    """
    Cache semântico baseado em JSON.

    Estrutura:

    respostas/
        bsi/
            resp-bsi.json

        civil/
            resp-civil.json


    Cada JSON:

    [
        {
            "pergunta": "...",
            "resposta": "..."
        }
    ]


    O FAISS é reconstruído automaticamente
    a partir desses arquivos.
    """



    def __init__(self):

        self.indices = {}

        os.makedirs(
            CACHE_DIR,
            exist_ok=True
        )

        os.makedirs(
            RESPOSTAS_DIR,
            exist_ok=True
        )


        self.reconstruir_todos_indices()


    # CAMINHOS
    def _caminho_indice(self, curso):

        return os.path.join(

            CACHE_DIR,

            curso

        )



    def _caminho_json(self, curso):

        return os.path.join(

            RESPOSTAS_DIR,

            curso,

            f"resp-{curso}.json"

        )




    
    # JSON
    def _carregar_json(self, curso):

        caminho = self._caminho_json(
            curso
        )


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



            return json.loads(
                conteudo
            )


    def _salvar_json(self, curso, dados):


        caminho = self._caminho_json(
            curso
        )


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




    
    # RECONSTRUÇÃO FAISS
    def _reconstruir_indice(self, curso):

        dados = self._carregar_json(
            curso
        )

        caminho = self._caminho_indice(
            curso
        )



        if not dados:

            if os.path.exists(caminho):

                shutil.rmtree(
                    caminho
                )


            self.indices.pop(
                curso,
                None
            )


            print(
                f"[CACHE] Índice removido: {curso}"
            )


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


        indice.save_local(
            caminho
        )


        self.indices[curso] = indice


        print(
            f"[CACHE] Índice reconstruído: {curso}"
        )


    def reconstruir_todos_indices(self):


        print(
            "[CACHE] Reconstruindo índices..."
        )


        if not os.path.exists(
            RESPOSTAS_DIR
        ):


            print(
                "[CACHE] Pasta respostas não encontrada."
            )


            return


        for curso in os.listdir(
            RESPOSTAS_DIR
        ):


            caminho = os.path.join(

                RESPOSTAS_DIR,

                curso

            )



            if os.path.isdir(caminho):


                self._reconstruir_indice(
                    curso
                )


        print(
            "[CACHE] Reconstrução concluída."
        )

    
    # CARREGAR FAISS
  
    def _carregar_indice(self, curso):


        if curso in self.indices:

            return self.indices[curso]



        caminho = self._caminho_indice(
            curso
        )



        if os.path.exists(caminho):


            print(
                f"[CACHE] Carregando índice: {curso}"
            )



            indice = FAISS.load_local(

                caminho,

                embeddings,

                allow_dangerous_deserialization=True

            )



            self.indices[curso] = indice



            return indice



        return None




    
    # BUSCA  
    def buscar(self, pergunta, curso):


        indice = self._carregar_indice(
            curso
        )


        if indice is None:

            return None


        resultados = indice.similarity_search_with_score(

            pergunta,

            k=1

        )



        if not resultados:

            return None


        documento, score = resultados[0]



        print(
            f"[CACHE] Distância: {score}"
        )


        if score <= LIMIAR_SIMILARIDADE:


            return documento.metadata.get(
                "resposta"
            )


        return None




    
    # SALVAR
    def salvar(self, pergunta, resposta, curso):


        dados = self._carregar_json(
            curso
        )


        for item in dados:


            if item["pergunta"] == pergunta:


                print(
                    "[CACHE] Pergunta já existe."
                )


                return


        dados.append({

            "pergunta": pergunta,

            "resposta": resposta

        })



        self._salvar_json(

            curso,

            dados

        )



        self._reconstruir_indice(
            curso
        )



        print(
            f"[CACHE] Salvo no JSON: {curso}"
        )


cache = SemanticCache()