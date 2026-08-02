import json
import os
import re
import unicodedata

from difflib import SequenceMatcher
from pathlib import Path
from datetime import datetime

from semantic_cache import cache

from config import (
    CURSOS,
    llm,
    retrievers,
    llm_compressor,
    USAR_COMPRESSAO_CONTEXTO
)

from prompts import (
    prompt_curso_template,
    prompt_memoria_template,
    prompt_principal_template,
    prompt_rerank_template,
    prompt_compressao_template,
    prompt_ementa_template
)


# ==========================
# CHAINS
# ==========================

chain_classificador = prompt_curso_template | llm
chain_memoria = prompt_memoria_template | llm
chain_rerank = prompt_rerank_template | llm
chain_resposta = prompt_principal_template | llm
chain_compressao = prompt_compressao_template | llm_compressor
chain_ementa = prompt_ementa_template | llm


# ==========================
# NORMALIZAÇÃO
# ==========================

def normalizar(texto):

    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    texto = texto.encode(
        "ASCII",
        "ignore"
    ).decode()

    texto = texto.lower()

    texto = re.sub(
        r"[^a-z0-9 ]",
        " ",
        texto
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    ).strip()

    return texto


# ==========================
# CLASSIFICAÇÃO DO CURSO
# ==========================

def classificar_curso(pergunta: str):

    resposta = chain_classificador.invoke({

        "question": pergunta

    })

    curso = resposta.content.strip().lower()

    if curso in retrievers:
        return curso

    return "geral"



# ==========================
# EXTRAÇÃO DE DISCIPLINA
# ==========================

def extrair_nome_disciplina(pergunta):

    resposta = chain_ementa.invoke({

        "question": pergunta

    })

    return resposta.content.strip()



# ==========================
# DETECÇÃO DE PDF
# ==========================

def usuario_pediu_pdf(texto):

    texto = texto.lower()

    palavras = [

        "ppc",
        "projeto pedagógico",
        "projeto pedagogico",
        "pdf",
        "baixar",
        "documento do curso"

    ]

    return any(
        palavra in texto
        for palavra in palavras
    )



# ==========================
# DETECÇÃO DE EMENTA
# ==========================

def usuario_pediu_ementa(texto):

    texto = texto.lower()

    palavras = [

        "ementa",
        "programa da disciplina",
        "conteúdo da disciplina",
        "conteudo da disciplina",
        "me envie a ementa",
        "mande a ementa"

    ]

    return any(
        palavra in texto
        for palavra in palavras
    )



# ==========================
# BUSCA DE IMAGEM DE EMENTA
# ==========================

def procurar_ementa(curso, disciplina):

    pasta = CURSOS[curso]["ementas"]

    if pasta is None:
        return None


    pasta = Path(pasta)


    if not pasta.exists():
        return None


    melhor = None
    melhor_score = 0


    for arquivo in pasta.glob("*.jpg"):

        nome = arquivo.stem


        nome = re.sub(
            r"^[A-Z]{2,5}\d+[_-]?",
            "",
            nome
        )


        score = SequenceMatcher(

            None,

            normalizar(disciplina),

            normalizar(nome)

        ).ratio()



        if score > melhor_score:

            melhor_score = score

            melhor = arquivo



    if melhor_score > 0.55:

        return str(melhor)


    return None



# ==========================
# MEMÓRIA
# ==========================

def decidir_uso_memoria(pergunta, historico):

    if not historico:
        return False


    historico_formatado = ""


    for mensagem in historico:

        role = (

            "Usuário"

            if mensagem["role"] == "user"

            else "Assistente"

        )


        historico_formatado += (

            f"{role}: {mensagem['content']}\n"

        )



    resposta = chain_memoria.invoke({

        "history": historico_formatado,

        "question": pergunta

    })


    return resposta.content.strip().upper() == "SIM"

# ==========================
# RECUPERAÇÃO DE DOCUMENTOS
# ==========================

def recuperar_documentos(curso, pergunta):

    retriever = retrievers[curso]

    documentos = retriever.invoke(
        pergunta
    )

    return documentos



# ==========================
# RERANK
# ==========================

def rerank_documentos(pergunta, documentos):

    if len(documentos) <= 4:

        return documentos


    docs_formatados = ""


    for i, doc in enumerate(documentos):

        docs_formatados += (

            f"[{i}] {doc.page_content}\n\n"

        )



    resposta = chain_rerank.invoke({

        "question": pergunta,

        "docs": docs_formatados

    })



    try:

        indices = re.findall(
            r"\d+",
            resposta.content
        )


        indices = [

            int(i)

            for i in indices

        ]


        documentos_filtrados = [

            documentos[i]

            for i in indices

            if i < len(documentos)

        ]



        if len(documentos_filtrados) == 0:

            documentos_filtrados = documentos[:3]



    except Exception:

        documentos_filtrados = documentos[:3]



    return documentos_filtrados




# ==========================
# CONTEXTO
# ==========================

def montar_contexto(documentos):

    return "\n\n".join(

        doc.page_content

        for doc in documentos

    )




# ==========================
# HISTÓRICO
# ==========================

def montar_historico(historico):

    historico_formatado = ""


    for mensagem in historico:

        role = (

            "Usuário"

            if mensagem["role"] == "user"

            else "Assistente"

        )


        historico_formatado += (

            f"{role}: {mensagem['content']}\n"

        )


    return historico_formatado




# ==========================
# LOGS
# ==========================

def registrar_log(
    pergunta,
    curso,
    documentos_recuperados,
    documentos_usados,
    contexto_comprimido,
    resposta
):

    log = {

        "timestamp": datetime.now().isoformat(),

        "pergunta": pergunta,

        "curso_classificado": curso,


        "documentos_recuperados": [

            {

                "conteudo": doc.page_content,

                "metadata": doc.metadata

            }

            for doc in documentos_recuperados

        ],


        "documentos_usados": [

            {

                "conteudo": doc.page_content,

                "metadata": doc.metadata

            }

            for doc in documentos_usados

        ],


        "contexto_comprimido": contexto_comprimido,


        "resposta": resposta

    }



    os.makedirs(
        "../../logs",
        exist_ok=True
    )



    with open(

        "../../logs/logs.jsonl",

        "a",

        encoding="utf-8"

    ) as arquivo:


        arquivo.write(

            json.dumps(

                log,

                ensure_ascii=False

            )

            + "\n"

        )





# ==========================
# COMPRESSÃO DE CONTEXTO
# ==========================

def comprimir_contexto(pergunta, contexto):

    print("\nANTES:")

    print(len(contexto))


    resposta = chain_compressao.invoke({

        "question": pergunta,

        "context": contexto

    })


    print("\nDEPOIS:")

    print(len(resposta.content))


    return resposta.content

# ==========================
# RESPOSTA PRINCIPAL
# ==========================

def responder(pergunta, historico=None):

    if historico is None:

        historico = []


    # Classificação do curso

    curso = classificar_curso(
        pergunta
    )


    # ==========================
    # CACHE SEMÂNTICO JSON
    # ==========================

    resposta_cache = cache.buscar(
        pergunta,
        curso
    )


    if resposta_cache is not None:

        print(
            "[CACHE] Resposta retornada."
        )


        return {

            "texto": resposta_cache,

            "arquivo": None,

            "tipo": None

        }



    # ==========================
    # EMENTAS (IMAGEM)
    # ==========================

    if usuario_pediu_ementa(
        pergunta
    ):


        disciplina = extrair_nome_disciplina(
            pergunta
        )


        imagem = procurar_ementa(

            curso,

            disciplina

        )



        if imagem:


            return {

                "texto": (
                    f"Segue a ementa da disciplina {disciplina}."
                ),

                "arquivo": imagem,

                "tipo": "imagem"

            }



        return {

            "texto": (
                "Não encontrei a ementa dessa disciplina."
            ),

            "arquivo": None,

            "tipo": None

        }




    # ==========================
    # PPC PDF
    # ==========================

    if usuario_pediu_pdf(
        pergunta
    ):


        caminho_pdf = CURSOS.get(
            curso,
            {}
        ).get(
            "pdf"
        )



        if caminho_pdf and os.path.exists(
            caminho_pdf
        ):


            return {

                "texto": (
                    "Segue o Projeto Pedagógico do Curso solicitado."
                ),

                "arquivo": caminho_pdf,

                "tipo": "pdf"

            }



        return {

            "texto": (
                "Não encontrei o PPC desse curso."
            ),

            "arquivo": None,

            "tipo": None

        }




    # ==========================
    # RECUPERAÇÃO RAG
    # ==========================

    documentos_recuperados = recuperar_documentos(

        curso,

        pergunta

    )



    # Rerank desativado

    documentos_usados = documentos_recuperados




    # ==========================
    # CONTEXTO
    # ==========================

    contexto_original = montar_contexto(

        documentos_usados

    )


    contexto_comprimido = contexto_original



    if USAR_COMPRESSAO_CONTEXTO:


        contexto_comprimido = comprimir_contexto(

            pergunta,

            contexto_original

        )




    # ==========================
    # MEMÓRIA
    # ==========================

    historico_formatado = ""



    if decidir_uso_memoria(

        pergunta,

        historico

    ):


        historico_formatado = montar_historico(

            historico

        )




    print(
        "\n========== CONTEXTO ENVIADO =========="
    )

    print(
        contexto_comprimido
    )

    print(
        "======================================"
    )




    # ==========================
    # GERAÇÃO DA RESPOSTA
    # ==========================

    resposta = chain_resposta.invoke({

        "context": contexto_comprimido,

        "history": historico_formatado,

        "question": pergunta

    })




    # ==========================
    # LOG
    # ==========================

    registrar_log(

        pergunta=pergunta,

        curso=curso,

        documentos_recuperados=documentos_recuperados,

        documentos_usados=documentos_usados,

        resposta=resposta.content,

        contexto_comprimido=contexto_comprimido

    )




    # ==========================
    # SALVAR NO CACHE JSON
    # ==========================

    cache.salvar(

        pergunta,

        resposta.content,

        curso

    )




    return {

        "texto": resposta.content,

        "arquivo": None,

        "tipo": None

    }
