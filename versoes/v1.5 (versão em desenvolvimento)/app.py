print("1 - app.py iniciou")
from collections import defaultdict

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import TOKEN
from rag import responder
print("2 - imports carregados")

# Histórico de cada usuário
historicos = defaultdict(list)


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mensagem = (
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

    await update.message.reply_text(mensagem)


# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    texto = (
        "Exemplos de perguntas:\n\n"
        "• Qual a carga horária do BSI?\n"
        "• Me envie o PPC de Engenharia Civil.\n"
        "• Quantos semestres possui Engenharia Elétrica?\n"
        "• Onde fica a biblioteca?\n"
        "• Qual o horário da secretaria?"
    )

    await update.message.reply_text(texto)


# Mensagens
async def mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    pergunta = update.message.text

    historico = historicos[chat_id]

    try:

        resposta = responder(
            pergunta,
            historico
        )

        # salva pergunta do usuário
        historico.append({
            "role": "user",
            "content": pergunta
        })

        # envia texto
        await update.message.reply_text(
            resposta["texto"]
        )

        # salva resposta
        historico.append({
            "role": "assistant",
            "content": resposta["texto"]
        })

        # envia PDF se existir
        if resposta["arquivo"] is not None:

            with open(resposta["arquivo"], "rb") as arquivo:

                if resposta.get("tipo") == "imagem":

                    await update.message.reply_photo(
                        photo=arquivo
                    )

                else:

                    await update.message.reply_document(
                        document=arquivo
                    )

    except Exception as erro:

        print(erro)

        await update.message.reply_text(
            "Ocorreu um erro ao processar sua solicitação."
        )


# Main
def main():
    print("3 - entrando no main()")
    
    app = Application.builder().token(TOKEN).build()
    print("4 - aplicação Telegram criada")
    app.add_handler(
        CommandHandler("start", start)
    )
    
    app.add_handler(
        CommandHandler("help", help_command)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            mensagem
        )
    )
    print("5 - handlers registrados")

    print("=" * 60)
    print("Bot iniciado.")
    print("=" * 60)

    app.run_polling()
    print("6 - polling encerrado")

if __name__ == "__main__":
    main()