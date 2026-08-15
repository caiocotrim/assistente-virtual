print("1 - whatsapp.py iniciou")

import os
import base64
import mimetypes

import requests

from collections import defaultdict
from pathlib import Path
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from rag import responder

print("2 - imports carregados")


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


EVOLUTION_URL = os.getenv(
    "EVOLUTION_URL",
    "http://localhost:8080"
).rstrip("/")


EVOLUTION_API_KEY = os.getenv(
    "EVOLUTION_API_KEY"
)


EVOLUTION_INSTANCE = os.getenv(
    "EVOLUTION_INSTANCE",
    "assistente-ifba"
)


# Números que o bot tem permissão de responder.
# Defina no .env como NUMEROS_PERMITIDOS=5577999999999,5577888888888
# (apenas dígitos, com DDI+DDD). Deixe vazio para responder a todos.
NUMEROS_PERMITIDOS = [
    numero.strip()
    for numero in os.getenv("NUMEROS_PERMITIDOS", "").split(",")
    if numero.strip()
]


# ============================================================
# FLASK
# ============================================================

app = Flask(__name__)


# ============================================================
# HISTÓRICO DE CADA USUÁRIO
# ============================================================

historicos = defaultdict(list)


# ============================================================
# MENSAGENS
# ============================================================

MENSAGEM_INICIAL = (
    "Olá! 👋\n\n"
    "Sou o Assistente Virtual Acadêmico do IFBA.\n\n"
    "Posso responder dúvidas sobre:\n"
    "• Cursos\n"
    "• PPC\n"
    "• Matriz curricular\n"
    "• Disciplinas\n"
    "• Calendário\n"
    "• Informações institucionais\n\n"
    "Basta enviar sua pergunta."
)


MENSAGEM_AJUDA = (
    "Exemplos de perguntas:\n\n"
    "• Qual a carga horária do BSI?\n"
    "• Me envie o PPC de Engenharia Civil.\n"
    "• Quantos semestres possui Engenharia Elétrica?\n"
    "• Onde fica a biblioteca?\n"
    "• Qual o horário da secretaria?"
)


# ============================================================
# NÚMERO
# ============================================================

def extrair_numero(jid):
    """
    A Evolution API entrega o remetente no formato de JID
    (ex: "5577999999999@s.whatsapp.net"), mas os endpoints de
    envio (sendText/sendMedia) esperam apenas os dígitos.
    """

    return jid.split("@")[0]


# ============================================================
# ENVIO DE TEXTO
# ============================================================

def enviar_texto(numero, texto):

    url = (
        f"{EVOLUTION_URL}"
        f"/message/sendText/"
        f"{EVOLUTION_INSTANCE}"
    )

    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "number": extrair_numero(numero),
        "text": texto
    }

    print(
        f"[WHATSAPP] Enviando texto para {numero}"
    )

    resposta = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )

    resposta.raise_for_status()

    print(
        f"[WHATSAPP] Texto enviado para {numero}"
    )

    return resposta.json()


# ============================================================
# ENVIO DE MÍDIA
# ============================================================

def enviar_midia(
    numero,
    caminho,
    tipo,
    legenda=None
):

    if not os.path.exists(caminho):

        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )


    # --------------------------------------------------------
    # MIME TYPE
    # --------------------------------------------------------

    mime_type, _ = mimetypes.guess_type(
        caminho
    )


    if mime_type is None:

        if tipo == "imagem":
            mime_type = "image/jpeg"

        elif tipo == "pdf":
            mime_type = "application/pdf"

        else:
            mime_type = "application/octet-stream"


    # --------------------------------------------------------
    # TIPO EVOLUTION
    # --------------------------------------------------------

    if tipo == "imagem":

        mediatype = "image"

    elif tipo == "pdf":

        mediatype = "document"

    else:

        raise ValueError(
            f"Tipo de mídia não suportado: {tipo}"
        )


    # --------------------------------------------------------
    # ARQUIVO
    # --------------------------------------------------------

    with open(
        caminho,
        "rb"
    ) as arquivo:

        conteudo = arquivo.read()


    base64_media = base64.b64encode(
        conteudo
    ).decode("utf-8")


    # --------------------------------------------------------
    # PAYLOAD
    # --------------------------------------------------------

    payload = {

        "number": extrair_numero(numero),

        "mediatype": mediatype,

        "mimetype": mime_type,

        "media": base64_media,

        "fileName": os.path.basename(
            caminho
        )
    }


    if legenda:

        payload["caption"] = legenda


    headers = {

        "apikey": EVOLUTION_API_KEY,

        "Content-Type": "application/json"
    }


    url = (
        f"{EVOLUTION_URL}"
        f"/message/sendMedia/"
        f"{EVOLUTION_INSTANCE}"
    )


    print(
        f"[WHATSAPP] Enviando {tipo} para {numero}"
    )

    print(
        f"[WHATSAPP] Arquivo: {caminho}"
    )


    resposta = requests.post(

        url,

        headers=headers,

        json=payload,

        timeout=120

    )


    resposta.raise_for_status()


    print(
        f"[WHATSAPP] {tipo.capitalize()} enviado para {numero}"
    )


    return resposta.json()


# ============================================================
# EXTRAIR TEXTO DA MENSAGEM
# ============================================================

def extrair_texto(mensagem):

    # --------------------------------------------------------
    # Mensagem de texto normal
    # --------------------------------------------------------

    texto = mensagem.get(
        "conversation"
    )


    if texto:

        return texto


    # --------------------------------------------------------
    # Mensagem de texto estendida
    # --------------------------------------------------------

    texto_estendido = (
        mensagem
        .get(
            "extendedTextMessage",
            {}
        )
        .get(
            "text"
        )
    )


    if texto_estendido:

        return texto_estendido


    return None


# ============================================================
# EXTRAIR DADOS DO WEBHOOK
# ============================================================

def extrair_mensagem(dados):

    data = dados.get(
        "data",
        {}
    )


    key = data.get(
        "key",
        {}
    )


    mensagem = data.get(
        "message",
        {}
    )


    # --------------------------------------------------------
    # Ignorar mensagens enviadas pelo próprio bot
    # --------------------------------------------------------

    if key.get("fromMe"):

        print(
            "[WHATSAPP] Mensagem enviada pelo próprio bot. Ignorando."
        )

        return None


    # --------------------------------------------------------
    # JID
    # --------------------------------------------------------

    remote_jid = key.get(
        "remoteJid"
    )


    if not remote_jid:

        return None


    # --------------------------------------------------------
    # IGNORAR GRUPOS
    # --------------------------------------------------------

    if remote_jid.endswith(
        "@g.us"
    ):

        print(
            f"[WHATSAPP] Mensagem de grupo ignorada: {remote_jid}"
        )

        return None


    # --------------------------------------------------------
    # TEXTO
    # --------------------------------------------------------

    texto = extrair_texto(
        mensagem
    )


    if not texto:

        print(
            "[WHATSAPP] Mensagem sem texto. Ignorando."
        )

        return None


    return {

        "jid": remote_jid,

        "numero": remote_jid,

        "texto": texto,

        "mensagem": mensagem,

        "key": key
    }


# ============================================================
# WEBHOOK
# ============================================================

@app.route(
    "/webhook",
    methods=["POST"]
)
def webhook():

    dados = request.get_json(
        silent=True
    )


    # --------------------------------------------------------
    # Payload inválido
    # --------------------------------------------------------

    if not dados:

        print(
            "[WEBHOOK] Payload vazio."
        )

        return jsonify({

            "status": "ignored",

            "motivo": "payload vazio"

        })


    print("\n" + "=" * 60)

    print(
        "[WEBHOOK] Evento recebido"
    )

    print("=" * 60)


    # --------------------------------------------------------
    # EVENTO
    # --------------------------------------------------------

    evento = dados.get(
        "event",
        ""
    ).lower()


    print(
        f"[WEBHOOK] Evento: {evento}"
    )


    if evento != "messages.upsert":

        print(
            "[WEBHOOK] Evento ignorado."
        )


        return jsonify({

            "status": "ignored",

            "evento": evento

        })


    # --------------------------------------------------------
    # EXTRAIR MENSAGEM
    # --------------------------------------------------------

    mensagem = extrair_mensagem(
        dados
    )


    if mensagem is None:

        return jsonify({

            "status": "ignored"

        })


    jid = mensagem["jid"]

    numero = mensagem["numero"]

    pergunta = mensagem["texto"]


    # --------------------------------------------------------
    # FILTRO DE NÚMEROS PERMITIDOS
    # --------------------------------------------------------

    if NUMEROS_PERMITIDOS and extrair_numero(numero) not in NUMEROS_PERMITIDOS:

        print(
            f"[WHATSAPP] Número não autorizado, ignorando: {numero}"
        )

        return jsonify({

            "status": "ignored",

            "motivo": "numero nao autorizado"

        })


    print(
        f"[WHATSAPP] Usuário: {numero}"
    )

    print(
        f"[WHATSAPP] Pergunta: {pergunta}"
    )


    # ========================================================
    # /start
    # ========================================================

    if pergunta.strip().lower() == "/start":

        try:

            enviar_texto(
                numero,
                MENSAGEM_INICIAL
            )

        except Exception as erro:

            print(
                f"[ERRO] Falha ao enviar /start: {erro}"
            )

            return jsonify({

                "status": "error"

            }), 500


        return jsonify({

            "status": "success"

        })


    # ========================================================
    # /help
    # ========================================================

    if pergunta.strip().lower() in [
        "/help",
        "ajuda"
    ]:

        try:

            enviar_texto(
                numero,
                MENSAGEM_AJUDA
            )

        except Exception as erro:

            print(
                f"[ERRO] Falha ao enviar /help: {erro}"
            )

            return jsonify({

                "status": "error"

            }), 500


        return jsonify({

            "status": "success"

        })


    # ========================================================
    # HISTÓRICO
    # ========================================================

    historico = historicos[
        jid
    ]


    print(
        f"[MEMÓRIA] Histórico atual: "
        f"{len(historico)} mensagens"
    )


    # ========================================================
    # RAG
    # ========================================================

    try:

        resposta = responder(

            pergunta,

            historico

        )


    except Exception as erro:

        print(
            "[ERRO] Falha no RAG:"
        )

        print(
            erro
        )


        try:

            enviar_texto(

                numero,

                "Ocorreu um erro ao processar sua solicitação."

            )

        except Exception as erro_envio:

            print(
                "[ERRO] Também falhou o envio "
                "da mensagem de erro:"
            )

            print(
                erro_envio
            )


        return jsonify({

            "status": "error"

        }), 500


    # ========================================================
    # SALVAR PERGUNTA
    # ========================================================

    historico.append({

        "role": "user",

        "content": pergunta

    })


    # ========================================================
    # TEXTO DA RESPOSTA
    # ========================================================

    texto_resposta = resposta.get(
        "texto"
    )


    if texto_resposta:

        try:

            enviar_texto(

                numero,

                texto_resposta

            )

        except Exception as erro:

            print(
                "[ERRO] Falha ao enviar resposta:"
            )

            print(
                erro
            )

            return jsonify({

                "status": "error"

            }), 500


    # ========================================================
    # SALVAR RESPOSTA NO HISTÓRICO
    # ========================================================

    if texto_resposta:

        historico.append({

            "role": "assistant",

            "content": texto_resposta

        })


    # ========================================================
    # ARQUIVO
    # ========================================================

    arquivo = resposta.get(
        "arquivo"
    )


    tipo = resposta.get(
        "tipo"
    )


    if arquivo:

        print(
            "[WHATSAPP] Resposta contém arquivo."
        )

        print(
            f"[WHATSAPP] Arquivo: {arquivo}"
        )

        print(
            f"[WHATSAPP] Tipo: {tipo}"
        )


        try:

            enviar_midia(

                numero,

                arquivo,

                tipo

            )

        except Exception as erro:

            print(
                "[ERRO] Falha ao enviar arquivo:"
            )

            print(
                erro
            )


    # ========================================================
    # FINAL
    # ========================================================

    print(
        "[WHATSAPP] Mensagem processada com sucesso."
    )

    print("=" * 60)


    return jsonify({

        "status": "success"

    })


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "3 - entrando no main()"
    )


    print(
        f"Evolution API: {EVOLUTION_URL}"
    )


    print(
        f"Instância: {EVOLUTION_INSTANCE}"
    )


    if not EVOLUTION_API_KEY:

        print(
            "[AVISO] EVOLUTION_API_KEY não configurada."
        )


    print(
        "4 - aplicação Flask criada"
    )


    print(
        "5 - webhook registrado: /webhook"
    )


    print("=" * 60)

    print(
        "Bot WhatsApp iniciado."
    )

    print("=" * 60)


    print(
        "Webhook:"
    )

    print(
        "http://0.0.0.0:5000/webhook"
    )


    print("=" * 60)


    app.run(

        host="0.0.0.0",

        port=5000,

        debug=False

    )


    print(
        "6 - servidor Flask encerrado"
    )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    main()