import json
import os
import re

from semantic_cache import cache

from datetime import datetime

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
    prompt_compressao_template
)


# CHAINS
chain_classificador = prompt_curso_template | llm
chain_memoria = prompt_memoria_template | llm
chain_rerank = prompt_rerank_template | llm
chain_resposta = prompt_principal_template | llm
chain_compressao = prompt_compressao_template | llm_compressor

# CLASSIFICAÇÃO DO CURSO
def classificar_curso(pergunta: str):
    """
    Classifica a pergunta em um dos cursos existentes.
    """

    resposta = chain_classificador.invoke({
        "question": pergunta
    })

    curso = resposta.content.strip().lower()

    if curso in retrievers:
        return curso

    return "geral"


# DETECÇÃO DE PEDIDO DE PDF
def usuario_pediu_pdf(texto: str):

    texto = texto.lower()

    palavras = [

        "ppc",

        "projeto pedagógico",

        "projeto pedagogico",

        "pdf",

        "envie",

        "me envie",

        "mande",

        "baixar",

        "documento do curso"

    ]

    return any(p in texto for p in palavras)


# DECISÃO DE USO DA MEMÓRIA
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

# RECUPERAÇÃO DE DOCUMENTOS
def recuperar_documentos(curso, pergunta):
    """
    Recupera documentos do índice FAISS correspondente ao curso.
    """

    retriever = retrievers[curso]

    documentos = retriever.invoke(pergunta)

    return documentos


# RERANK
def rerank_documentos(pergunta, documentos):
    """
    Seleciona os documentos mais relevantes utilizando o LLM.
    """

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

        indices = re.findall(r"\d+", resposta.content)

        indices = [int(i) for i in indices]

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


# FORMATAÇÃO DO CONTEXTO
def montar_contexto(documentos):
    """
    Concatena os documentos selecionados em uma única string.
    """

    return "\n\n".join(

        doc.page_content

        for doc in documentos

    )


# FORMATAÇÃO DO HISTÓRICO
def montar_historico(historico):
    """
    Converte o histórico do chat em texto para enviar ao prompt.
    """

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


# LOGS
def registrar_log(
    pergunta,
    curso,
    documentos_recuperados,
    documentos_usados,
    contexto_comprimido,
    resposta
):
    """
    Salva um log da interação.
    """

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

    os.makedirs("../../logs", exist_ok=True)

    with open(
        "../../logs/logs.jsonl",
        "a",
        encoding="utf-8"
    ) as arquivo:

        arquivo.write(
            json.dumps(
                log,
                ensure_ascii=False
            ) + "\n"
        )

# COMPRIME CONTEXTO PARA LLM GERAR RESPOSTA FINAL
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

# RESPOSTA PRINCIPAL
def responder(pergunta, historico=None):

    if historico is None:
        historico = []

    # Classificação do curso
    curso = classificar_curso(pergunta)

    # Pedido de PDF
    if usuario_pediu_pdf(pergunta):

        caminho_pdf = CURSOS.get(curso, {}).get("pdf")

        if caminho_pdf and os.path.exists(caminho_pdf):

            return {

                "texto": "Segue o Projeto Pedagógico do Curso solicitado.",

                "arquivo": caminho_pdf

            }

        return {

            "texto": "Não encontrei o PPC desse curso.",

            "arquivo": None

        }

    # Cache semântico
    resposta_cache = cache.buscar(pergunta, curso)

    if resposta_cache is not None:

        print("[CACHE] Resposta retornada.")

        return {

            "texto": resposta_cache,

            "arquivo": None

        }

    # Recuperação
    documentos_recuperados = recuperar_documentos(
        curso,
        pergunta
    )
    """
    RERANK DESATIVADO PARA TESTE
    # Rerank
    documentos_usados = rerank_documentos(
        pergunta,
        documentos_recuperados
    )
    """

    # Substituição do rerank
    documentos_usados = documentos_recuperados

    # Contexto
    contexto_original = montar_contexto(
        documentos_usados
    )

    contexto_comprimido = contexto_original


    if USAR_COMPRESSAO_CONTEXTO:

        contexto_comprimido = comprimir_contexto(
            pergunta,
            contexto_original
        )

    # Memória
    historico_formatado = ""

    if decidir_uso_memoria(
        pergunta,
        historico
    ):

        historico_formatado = montar_historico(
            historico
        )

    print("\n========== CONTEXTO ENVIADO ==========")
    print(contexto_comprimido)
    print("======================================")
    # Resposta do modelo
    resposta = chain_resposta.invoke({

        "context": contexto_comprimido,

        "history": historico_formatado,

        "question": pergunta

    })

    # Log
    registrar_log(

        pergunta=pergunta,

        curso=curso,

        documentos_recuperados=documentos_recuperados,

        documentos_usados=documentos_usados,

        resposta=resposta.content,

        contexto_comprimido=contexto_comprimido

    )

    cache.salvar(

        pergunta,

        resposta.content,

        curso

    )

    # Retorno
    return {

        "texto": resposta.content,

        "arquivo": None

    }